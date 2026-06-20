# Troubleshooting Steps By Scenario

Use these labs one by one. Do not apply all broken scenarios at once in the beginning. Practice like a production incident: create one failure, observe symptoms, isolate root cause, fix, validate, and clean up.

## 1. Pod: ImagePullBackOff

Create the issue:

```bash
kubectl apply -f scenarios/pods/01-imagepullbackoff/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
ImagePullBackOff
ErrImagePull
```

Troubleshoot:

```bash
kubectl describe pod -n troubleshooting-lab -l app=imagepull-demo
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
```

Root cause:

The image tag `nginx:this-tag-does-not-exist` is invalid.

Fix:

```bash
kubectl apply -f scenarios/pods/01-imagepullbackoff/fixed.yaml
kubectl rollout status deploy/imagepull-demo -n troubleshooting-lab
```

## 2. Pod: CrashLoopBackOff

Create the issue:

```bash
kubectl apply -f scenarios/pods/02-crashloopbackoff/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=crashloop-demo -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD" -n troubleshooting-lab
kubectl logs "$POD" --previous -n troubleshooting-lab
kubectl describe pod "$POD" -n troubleshooting-lab
```

Root cause:

The container command exits with status code `1`.

Fix:

```bash
kubectl apply -f scenarios/pods/02-crashloopbackoff/fixed.yaml
kubectl rollout status deploy/crashloop-demo -n troubleshooting-lab
```

## 3. Pod: CreateContainerConfigError

Create the issue:

```bash
kubectl apply -f scenarios/pods/03-createcontainerconfigerror/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=missing-config-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get cm -n troubleshooting-lab
```

Root cause:

The pod references a ConfigMap named `app-runtime-config`, but that ConfigMap does not exist.

Fix:

```bash
kubectl apply -f scenarios/pods/03-createcontainerconfigerror/fixed.yaml
kubectl rollout status deploy/missing-config-demo -n troubleshooting-lab
```

## 4. Init Container: Waiting For Missing Service

Create the issue:

```bash
kubectl apply -f scenarios/init-containers/01-init-waiting-for-service/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
Init:0/1
PodInitializing
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=init-wait-demo -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD" -c wait-for-db -n troubleshooting-lab
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get svc -n troubleshooting-lab
```

Root cause:

The init container waits for `payments-db.troubleshooting-lab.svc.cluster.local`, but the service does not exist.

Fix:

```bash
kubectl apply -f scenarios/init-containers/01-init-waiting-for-service/fixed.yaml
kubectl rollout status deploy/payments-db -n troubleshooting-lab
kubectl rollout status deploy/init-wait-demo -n troubleshooting-lab
```

## 5. Deployment: Rollout Stuck Due To Readiness Probe

Create the issue:

```bash
kubectl apply -f scenarios/deployments/01-readiness-rollout-stuck/broken.yaml
kubectl rollout status deploy/readiness-demo -n troubleshooting-lab
```

Troubleshoot:

```bash
kubectl get deploy readiness-demo -n troubleshooting-lab
kubectl describe deploy readiness-demo -n troubleshooting-lab
kubectl get pods -n troubleshooting-lab -l app=readiness-demo
POD=$(kubectl get pod -n troubleshooting-lab -l app=readiness-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
```

Root cause:

The readiness probe checks `/missing-health-page`, but nginx serves `/`.

Fix:

```bash
kubectl apply -f scenarios/deployments/01-readiness-rollout-stuck/fixed.yaml
kubectl rollout status deploy/readiness-demo -n troubleshooting-lab
```

## 6. Networking: Service Selector Mismatch

Create the issue:

```bash
kubectl apply -f scenarios/networking/01-service-selector-mismatch/broken.yaml
kubectl get svc,endpoints -n troubleshooting-lab
```

Expected symptom:

```text
selector-backend   <none>
```

Troubleshoot:

```bash
kubectl get pods -n troubleshooting-lab --show-labels
kubectl describe svc selector-backend -n troubleshooting-lab
kubectl get endpoints selector-backend -n troubleshooting-lab
kubectl exec -n troubleshooting-lab netshoot -- curl -v http://selector-backend.troubleshooting-lab.svc.cluster.local
```

Root cause:

The service selector is `app=selector-backend-wrong`, but the pods have `app=selector-backend`.

Fix:

```bash
kubectl apply -f scenarios/networking/01-service-selector-mismatch/fixed.yaml
kubectl get endpoints selector-backend -n troubleshooting-lab
kubectl exec -n troubleshooting-lab netshoot -- curl -s http://selector-backend.troubleshooting-lab.svc.cluster.local
```

## 7. Networking: Wrong targetPort

Create the issue:

```bash
kubectl apply -f scenarios/networking/02-wrong-targetport/broken.yaml
kubectl get svc,endpoints -n troubleshooting-lab
```

Troubleshoot:

```bash
kubectl describe svc targetport-api -n troubleshooting-lab
kubectl get endpoints targetport-api -n troubleshooting-lab
kubectl exec -n troubleshooting-lab netshoot -- curl -v http://targetport-api.troubleshooting-lab.svc.cluster.local
POD=$(kubectl get pod -n troubleshooting-lab -l app=targetport-api -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n troubleshooting-lab "$POD" -- netstat -tuln
```

Root cause:

The container listens on `8080`, but the Service sends traffic to `targetPort: 9090`.

Fix:

```bash
kubectl apply -f scenarios/networking/02-wrong-targetport/fixed.yaml
kubectl exec -n troubleshooting-lab netshoot -- curl -s http://targetport-api.troubleshooting-lab.svc.cluster.local
```

## 8. Scheduling: Node Selector Mismatch

Create the issue:

```bash
kubectl apply -f scenarios/scheduling/01-node-selector-mismatch/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=node-selector-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get nodes --show-labels
```

Root cause:

The pod asks for `nodeSelector: disktype=ssd`, but no Kind node has that label.

Fix option 1 - change the workload:

```bash
kubectl apply -f scenarios/scheduling/01-node-selector-mismatch/fixed.yaml
kubectl rollout status deploy/node-selector-demo -n troubleshooting-lab
```

Fix option 2 - add a node label:

```bash
kubectl label node troubleshooting-worker disktype=ssd
kubectl get pods -n troubleshooting-lab -o wide
```

