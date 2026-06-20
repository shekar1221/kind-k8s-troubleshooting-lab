# Scenario Cheat Table

| Area | Scenario | Expected Status / Symptom | Main Command | Root Cause | Fix File |
|---|---|---|---|---|---|
| Pod | ImagePullBackOff | `ImagePullBackOff`, `ErrImagePull` | `kubectl describe pod` | Wrong image tag | `scenarios/pods/01-imagepullbackoff/fixed.yaml` |
| Pod | CrashLoopBackOff | `CrashLoopBackOff` | `kubectl logs --previous` | Container exits with code 1 | `scenarios/pods/02-crashloopbackoff/fixed.yaml` |
| Pod | Missing ConfigMap env | `CreateContainerConfigError` | `kubectl describe pod` | ConfigMap does not exist | `scenarios/pods/03-createcontainerconfigerror/fixed.yaml` |
| Init Container | Wait for DB service | `Init:0/1` | `kubectl logs -c wait-for-db` | Service DNS does not exist | `scenarios/init-containers/01-init-waiting-for-service/fixed.yaml` |
| Deployment | Readiness probe failure | Rollout stuck | `kubectl rollout status` | Probe checks wrong path | `scenarios/deployments/01-readiness-rollout-stuck/fixed.yaml` |
| Network | Service selector mismatch | Endpoint is empty | `kubectl get endpoints` | Service selector does not match pod label | `scenarios/networking/01-service-selector-mismatch/fixed.yaml` |
| Network | Wrong targetPort | Curl fails though endpoint exists | `kubectl describe svc` | Service sends traffic to closed port | `scenarios/networking/02-wrong-targetport/fixed.yaml` |
| Volume | Missing ConfigMap volume | `ContainerCreating`, `FailedMount` | `kubectl describe pod` | ConfigMap volume source missing | `scenarios/volumes/01-missing-configmap-volume/fixed.yaml` |
| Volume | Wrong PVC StorageClass | `PVC Pending`, `Pod Pending` | `kubectl describe pvc` | StorageClass does not exist | `scenarios/volumes/02-pvc-wrong-storageclass/fixed.yaml` |
| Volume | Missing Secret volume | `ContainerCreating`, `FailedMount` | `kubectl describe pod` | Secret volume source missing | `scenarios/volumes/03-missing-secret-volume/fixed.yaml` |
| Volume | ConfigMap key missing | `ContainerCreating`, `FailedMount` | `kubectl get cm -o yaml` | Requested ConfigMap key does not exist | `scenarios/volumes/04-configmap-key-missing/fixed.yaml` |
| Volume | Read-only ConfigMap write | `CrashLoopBackOff` | `kubectl logs --previous` | App writes to read-only ConfigMap mount | `scenarios/volumes/05-readonly-configmap-write/fixed.yaml` |
| Volume | hostPath wrong type | `ContainerCreating`, `FailedMount` | `kubectl describe pod` | Required host directory does not exist | `scenarios/volumes/06-hostpath-wrong-type/fixed.yaml` |
| Volume | emptyDir data loss | New pod has new data | `kubectl exec cat /cache/start-time.txt` | `emptyDir` is pod lifecycle storage | `scenarios/volumes/07-emptydir-data-loss/demo.yaml` |
| Scheduling | Node selector mismatch | `Pending`, `FailedScheduling` | `kubectl describe pod` | No node has requested label | `scenarios/scheduling/01-node-selector-mismatch/fixed.yaml` |

## Interview Answer Pattern

Use this structure when explaining any issue:

1. Symptom: what users or monitoring saw.
2. Scope: one pod, one deployment, one namespace, or full cluster.
3. Evidence: events, logs, rollout status, endpoints, PVC, or node condition.
4. Root cause: exact wrong config or failed dependency.
5. Fix: YAML/GitOps correction.
6. Prevention: validation, alerts, readiness checks, CI/CD policy, or runbook.

