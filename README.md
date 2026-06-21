# Kind Kubernetes Troubleshooting Lab

This project creates a local Kubernetes troubleshooting lab using Kind with:

- 1 control-plane node
- 2 worker nodes
- A dedicated namespace named `troubleshooting-lab`
- Broken and fixed manifests for common production-style failures

The goal is to practice how to identify, explain, and fix failures in pods, deployments, services, init containers, volumes, PVCs, and scheduling.

## Documentation Map

| File | Purpose |
|---|---|
| `docs/TEST-SCENARIOS-WITH-COMMANDS.md` | Step-by-step test commands for each failure and fix |
| `docs/TROUBLESHOOTING-STEPS.md` | Troubleshooting workflow by scenario |
| `docs/VOLUMES-LAB.md` | Dedicated Kubernetes volumes practice guide |
| `docs/SCENARIO-CHEAT-TABLE.md` | Quick table of symptoms, causes, and fixes |
| `docs/INTERVIEW-QA-AND-PRESENTATION.md` | Interview answers and production story format |
| `scripts/health_check.py` | Python service health checker |

## Prerequisites

Install these tools on your laptop:

- Docker Desktop or Docker Engine
- Kind
- kubectl

Validate:

```bash
docker version
kind version
kubectl version --client
<<<<<<< HEAD
=======

kubectl config get-contexts
kubectl config current-context
kubectl config set-context --current --namespace=troubleshooting-lab
kubectl get pods

docker not running started by below command
PS C:\WINDOWS\system32> Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  or
PS C:\WINDOWS\system32> Start-Service com.docker.service
PS C:\WINDOWS\system32> Get-Service com.docker.service

Status   Name               DisplayName
------   ----               -----------
Running  com.docker.service Docker Desktop Service
>>>>>>> e5866f6f22980de78ab2e84579bf2ea89627cd9d
```

## Create The Kind Cluster

From the project root:

```bash
kind create cluster --config kind/cluster-2-workers.yaml
```

Validate the 3-node cluster:

```bash
kubectl get nodes -o wide
```

Expected:

```text
troubleshooting-control-plane   Ready
troubleshooting-worker          Ready
troubleshooting-worker2         Ready
```

## Install Base Resources

```bash
kubectl apply -f manifests/base/
kubectl get pods -n troubleshooting-lab
kubectl get svc -n troubleshooting-lab
```

Validate service connectivity:

```bash
kubectl exec -n troubleshooting-lab netshoot -- curl -s http://orders-api.troubleshooting-lab.svc.cluster.local
```

Run Python health check from inside the cluster:

```bash
kubectl exec -n troubleshooting-lab health-checker -- python /scripts/health_check.py
```

Run Python health check from your laptop for localhost/NodePort:

```bash
python scripts/health_check.py --target local-orders-api:localhost:8080:/
```

## How To Run Each Scenario

Each scenario has either:

- `broken.yaml`
- `fixed.yaml`

Run the broken file first:

```bash
kubectl apply -f scenarios/<category>/<scenario>/broken.yaml
```

Troubleshoot:

```bash
kubectl get pods -n troubleshooting-lab
kubectl describe pod <pod-name> -n troubleshooting-lab
kubectl logs <pod-name> -n troubleshooting-lab
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
```

Apply the fix:

```bash
kubectl apply -f scenarios/<category>/<scenario>/fixed.yaml
```

Validate:

```bash
kubectl get pods -n troubleshooting-lab
kubectl get deploy -n troubleshooting-lab
```

## Reset One Scenario

Delete only the resources from that scenario:

```bash
kubectl delete -f scenarios/<category>/<scenario>/broken.yaml --ignore-not-found
kubectl delete -f scenarios/<category>/<scenario>/fixed.yaml --ignore-not-found
```

Some volume scenarios create PVCs, Secrets, or ConfigMaps. Always check:

```bash
kubectl get all,cm,secret,pvc -n troubleshooting-lab
```

## Delete The Full Cluster

```bash
kind delete cluster --name troubleshooting
```

## Scenario Index

| Area | Scenario | Failure |
|---|---|---|
| Pods | `pods/01-imagepullbackoff` | Wrong image tag |
| Pods | `pods/02-crashloopbackoff` | Container exits after startup |
| Pods | `pods/03-createcontainerconfigerror` | Missing ConfigMap reference |
| Init Containers | `init-containers/01-init-waiting-for-service` | Init waits for missing service |
| Deployments | `deployments/01-readiness-rollout-stuck` | Readiness probe points to bad path |
| Networking | `networking/01-service-selector-mismatch` | Service selector does not match pod labels |
| Networking | `networking/02-wrong-targetport` | Service targetPort points to closed port |
| Volumes | `volumes/01-missing-configmap-volume` | ConfigMap volume source missing |
| Volumes | `volumes/02-pvc-wrong-storageclass` | PVC uses non-existing StorageClass |
| Volumes | `volumes/03-missing-secret-volume` | Secret volume source missing |
| Volumes | `volumes/04-configmap-key-missing` | ConfigMap exists but requested key is missing |
| Volumes | `volumes/05-readonly-configmap-write` | App tries to write into read-only ConfigMap volume |
| Volumes | `volumes/06-hostpath-wrong-type` | hostPath requires a directory that does not exist |
| Volumes | `volumes/07-emptydir-data-loss` | emptyDir data disappears when pod is recreated |
| Scheduling | `scheduling/01-node-selector-mismatch` | Pod requests a node label that does not exist |

## Recommended Practice Order

1. Read `docs/SCENARIO-CHEAT-TABLE.md`.
2. Run `docs/TEST-SCENARIOS-WITH-COMMANDS.md` scenario by scenario.
3. For storage practice, use `docs/VOLUMES-LAB.md`.
4. After each fix, run the Python health check.
5. Prepare interview stories using `docs/INTERVIEW-QA-AND-PRESENTATION.md`.

## Production Troubleshooting Flow

Use this order during interview and incident calls:

1. Check pod status.
2. Check pod events.
3. Check current and previous logs.
4. Check deployment rollout.
5. Check service endpoints.
6. Check DNS and target port.
7. Check PVC, PV, ConfigMap, Secret, and volume mounts.
8. Check node pressure and scheduling constraints.
9. Apply fix through YAML or GitOps, not only manual patching.

Commands:

```bash
kubectl get pods -n troubleshooting-lab
kubectl describe pod <pod-name> -n troubleshooting-lab
kubectl logs <pod-name> -n troubleshooting-lab
kubectl logs <pod-name> --previous -n troubleshooting-lab
kubectl get deploy -n troubleshooting-lab
kubectl rollout status deploy/<deployment-name> -n troubleshooting-lab
kubectl get svc,endpoints -n troubleshooting-lab
kubectl get cm,secret,pvc,pv -n troubleshooting-lab
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
```
