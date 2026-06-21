# Interview Q&A And Presentation Guide

Use this document to explain the lab like a real production issue.

## How To Present Any Kubernetes Issue

Use this structure:

1. Issue: what failed.
2. Business impact: who was affected.
3. Initial observation: what alert, dashboard, or user complaint showed.
4. Troubleshooting: commands and evidence.
5. Root cause: exact technical reason.
6. Fix: what changed.
7. Prevention: what you improved to avoid repeat.

Short format:

```bash
We observed [symptom]. I checked [events/logs/rollout/endpoints/PVC].
The root cause was [exact issue]. We fixed it by [fix].
To prevent recurrence, we added [alert/check/pipeline validation/runbook].
```

## 1. Pods

### Q1. A pod is in ImagePullBackOff. How do you troubleshoot?

Answer:

```bash
I first describe the pod and check events. ImagePullBackOff usually means Kubernetes cannot pull the container image. I validate the image name, tag, registry path, imagePullSecret, and registry access. If the image tag is wrong, I update the deployment manifest with the correct immutable image tag and redeploy through the approved pipeline or GitOps.
```

Commands:

```bash
kubectl get pods -n <ns>
kubectl describe pod <pod> -n <ns>
kubectl get events -n <ns> --sort-by='.lastTimestamp'
kubectl get secret -n <ns>
```

Production example:

```bash
After a payment API release, pods were stuck in ImagePullBackOff. Events showed image tag not found. The deployment used a wrong build tag. We corrected the image tag in Git, ArgoCD synced it, and pods became Running.
```

### Q2. A pod is in CrashLoopBackOff. What do you check?

Answer:

```bash
CrashLoopBackOff means the container starts and then exits repeatedly. I check current logs, previous logs, exit code, environment variables, ConfigMaps, Secrets, and dependency connectivity. Previous logs are important because the current container may not have useful logs after restart.
```

Commands:

```bash
kubectl logs <pod> -n <ns>
kubectl logs <pod> --previous -n <ns>
kubectl describe pod <pod> -n <ns>
kubectl get cm,secret -n <ns>
```

How to present:

```bash
The pod was restarting repeatedly. I used kubectl logs --previous and found the application was exiting because a required environment variable was missing. I created/fixed the ConfigMap and restarted the rollout.
```

### Q3. What is CreateContainerConfigError?

Answer:

```bash
CreateContainerConfigError happens before the container starts. It is usually caused by invalid pod configuration, such as missing ConfigMap, missing Secret, wrong env reference, or volume reference. Since the container did not start, logs may not help. Events from kubectl describe pod are more useful.
```

## 2. Deployments

### Q4. Deployment rollout is stuck. How do you troubleshoot?

Answer:

```bash
I check rollout status, deployment conditions, ReplicaSets, pod readiness, and events. A rollout commonly gets stuck because new pods fail readiness checks, crash, cannot pull images, or cannot mount volumes.
```

Commands:

```bash
kubectl rollout status deploy/<deploy> -n <ns>
kubectl describe deploy <deploy> -n <ns>
kubectl get rs -n <ns>
kubectl get pods -n <ns>
kubectl describe pod <pod> -n <ns>
```

Fix options:

```bash
kubectl rollout undo deploy/<deploy> -n <ns>
kubectl apply -f fixed.yaml
```

Production example:

```bash
A new application version was deployed, but rollout did not complete. The pods were running but not ready. Events showed readiness probe failure with HTTP 404. The health endpoint path changed in the new version. We updated the readiness probe path and redeployed.
```

### Q5. How do you avoid downtime during deployments?

Answer:

```bash
I use multiple replicas, readiness probes, rolling update strategy, PodDisruptionBudget, and proper resource requests. For critical applications, I prefer canary or blue-green deployments using Argo Rollouts or service mesh routing.
```

Important YAML:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

## 3. Services And Networking

### Q6. Service has no endpoints. What does it mean?

Answer:

```bash
It means the Service is not selecting any ready pod. Most common causes are selector and pod label mismatch, pods not ready, or pods running in a different namespace. I compare service selectors with pod labels.
```

Commands:

```bash
kubectl describe svc <svc> -n <ns>
kubectl get endpoints <svc> -n <ns>
kubectl get pods -n <ns> --show-labels
kubectl get endpointslice -n <ns>
```

Production example:

```bash
The frontend was getting 503 from backend service. Service DNS was resolving, but endpoints were empty. The service selector was app=orders-api, while the new deployment label was app=orders-v2. We corrected labels/selectors in GitOps and traffic recovered.
```

### Q7. DNS works but application connection fails. What next?

Answer:

```bash
If DNS resolves but connection fails, I check service targetPort, pod containerPort, app listen port, NetworkPolicy, and application logs. DNS only proves name resolution; it does not prove the application is listening.
```

Commands:

```bash
kubectl exec -n <ns> netshoot -- nslookup <svc>.<ns>.svc.cluster.local
kubectl exec -n <ns> netshoot -- curl -v http://<svc>.<ns>.svc.cluster.local:<port>
kubectl describe svc <svc> -n <ns>
kubectl get endpoints <svc> -n <ns>
```

### Q8. What is CoreDNS and when do you check it?

Answer:

```bash
CoreDNS provides internal DNS resolution in Kubernetes. I check CoreDNS when pods cannot resolve service names, external DNS names, or DNS latency is high. I verify CoreDNS pods, logs, resource usage, and test DNS from a debug pod.
```

Commands:

```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n kube-system logs deploy/coredns
kubectl exec -n <ns> netshoot -- nslookup kubernetes.default.svc.cluster.local
kubectl exec -n <ns> netshoot -- nslookup <service>.<namespace>.svc.cluster.local
```

Note:

```bash
Run nslookup from inside a pod, not from Windows Git Bash, when checking ClusterIP service DNS. ClusterIP service names exist only inside the Kubernetes cluster.
```

## 4. Volumes

### Q9. Pod is stuck in ContainerCreating. How can volume be the reason?

Answer:

```bash
ContainerCreating can happen when kubelet is waiting to mount a volume. I check pod events for FailedMount, then verify PVC, ConfigMap, Secret, StorageClass, and CSI driver status.
```

Commands:

```bash
kubectl describe pod <pod> -n <ns>
kubectl get pvc,pv,storageclass -n <ns>
kubectl get cm,secret -n <ns>
kubectl get events -n <ns> --sort-by='.lastTimestamp'
```

### Q10. PVC is Pending. What do you check?

Answer:

```bash
PVC Pending means storage is not bound. I check StorageClass name, dynamic provisioner, access mode, requested size, volume topology, and quota. In cloud, I also check CSI driver health and IAM permissions.
```

Production example:

```bash
A reporting pod was Pending after deployment. PVC was also Pending. The StorageClass name in YAML was wrong. We corrected the StorageClass and recreated the PVC because storageClassName is immutable.
```

### Q11. Why can an application fail with read-only file system on ConfigMap?

Answer:

```bash
ConfigMap and Secret volumes are mounted read-only. If the application tries to update files in that mounted path, it can crash. The fix is to copy the config into a writable emptyDir during startup, or change the application to write runtime files elsewhere.
```

## 5. PDB

### Q12. What is PDB?

Answer:

```bash
PDB means PodDisruptionBudget. It protects application availability during voluntary disruptions like node drain, cluster upgrade, and maintenance. It tells Kubernetes how many pods must remain available.
```

Example:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payments-api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: payments-api
```

Production issue:

```bash
During node patching, drain was stuck because deployment had 2 replicas and PDB required minAvailable 2. Kubernetes could not evict any pod. We scaled replicas to 3 before maintenance, then drained the node safely.
```

Commands:

```bash
kubectl get pdb -A
kubectl describe pdb <pdb> -n <ns>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
```

## 6. Application, Database, And Middleware

### Q13. Application returns 500 after deployment. How do you troubleshoot?

Answer:

```bash
I check whether the issue is application code, config, downstream dependency, database, or middleware. I review logs, recent ConfigMap/Secret changes, deployment revision, service endpoints, and traces if OpenTelemetry or Jaeger is available.
```

Commands:

```bash
kubectl logs deploy/<app> -n <ns> --tail=100
kubectl rollout history deploy/<app> -n <ns>
kubectl get cm,secret -n <ns>
kubectl get svc,endpoints -n <ns>
```

### Q14. Application cannot connect to database. What do you check?

Answer:

```bash
I verify database service DNS, port connectivity, credentials in Secret, NetworkPolicy, DB pod or managed DB health, and application connection pool logs.
```

Commands:

```bash
kubectl exec -n <ns> netshoot -- nslookup <db-service>.<ns>.svc.cluster.local
kubectl exec -n <ns> netshoot -- nc -vz <db-service>.<ns>.svc.cluster.local 5432
kubectl get secret -n <ns>
kubectl logs <app-pod> -n <ns>
```

If `nc` is not available:

```bash
kubectl exec -n <ns> netshoot -- curl -v telnet://<db-service>.<ns>.svc.cluster.local:5432
```

### Q15. Kafka consumer lag is high. How do you present it?

Answer:

```bash
We observed transaction processing delay. Kafka consumer lag increased, but API pods were healthy. I checked consumer pod logs, consumer group lag, CPU/memory, broker connectivity, and downstream database latency. We scaled consumers and fixed the slow downstream dependency.
```

Commands:

```bash
kubectl get pods -n kafka
kubectl get pods -n <app-ns>
kubectl logs deploy/<consumer-app> -n <app-ns> --tail=100
kubectl top pods -n <app-ns>
```

## 7. Strong Final Interview Story

Use this as a polished answer:

```bash
In one production-like issue, users were seeing failures from the orders service. I first checked pod health and deployment rollout. Pods were running, so I moved to service discovery. The service DNS resolved, but endpoints were empty. I compared the service selector with pod labels and found a mismatch introduced during deployment. The fix was to correct the selector in Git, let ArgoCD sync it, and validate using curl from a netshoot pod. We also added a CI validation step to check service selectors against deployment labels before merge.
```

## 8. Manager-Level Summary

```bash
The impact was application unavailability due to wrong Kubernetes service routing. We isolated the issue to configuration, not infrastructure. The fix was applied through the approved deployment process. As prevention, we improved manifest validation, monitoring on empty endpoints, and updated the runbook.
```

