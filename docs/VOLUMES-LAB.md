# Kubernetes Volumes Lab

Volumes are one of the most common reasons pods get stuck in `ContainerCreating`, `Pending`, `CreateContainerConfigError`, or `CrashLoopBackOff`.

Think of a volume like a folder attached to a container. The important part is where the folder comes from:

| Volume Type | Simple Meaning | Real Use |
|---|---|---|
| `emptyDir` | Temporary folder created with the pod | Cache, scratch files, temporary processing |
| `configMap` | Files created from ConfigMap data | App config files like `application.yaml` |
| `secret` | Files created from Secret data | Passwords, tokens, certificates |
| `persistentVolumeClaim` | Request for persistent storage | Database data, reports, uploads |
| `hostPath` | Folder from the Kubernetes node | Node logs, special local testing, not preferred for normal apps |

## Volume Troubleshooting Commands

```bash
kubectl get pods -n troubleshooting-lab
kubectl describe pod <pod-name> -n troubleshooting-lab
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
kubectl get cm,secret,pvc,pv,storageclass -n troubleshooting-lab
kubectl describe pvc <pvc-name> -n troubleshooting-lab
```

## 1. Missing ConfigMap Volume

Create the issue:

```bash
kubectl apply -f scenarios/volumes/01-missing-configmap-volume/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
ContainerCreating
FailedMount
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=volume-config-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get cm -n troubleshooting-lab
```

Root cause:

The pod wants a ConfigMap called `nginx-custom-config`, but it does not exist.

Fix:

```bash
kubectl apply -f scenarios/volumes/01-missing-configmap-volume/fixed.yaml
kubectl rollout status deploy/volume-config-demo -n troubleshooting-lab
```

## 2. PVC Wrong StorageClass

Create the issue:

```bash
kubectl apply -f scenarios/volumes/02-pvc-wrong-storageclass/broken.yaml
kubectl get pvc -n troubleshooting-lab
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
PVC Pending
Pod Pending
```

Troubleshoot:

```bash
kubectl describe pvc reports-pvc -n troubleshooting-lab
kubectl get storageclass
POD=$(kubectl get pod -n troubleshooting-lab -l app=reports-api -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
```

Root cause:

The PVC asks for `gold-storage-does-not-exist`. Kind normally provides a `standard` StorageClass.

Important:

`storageClassName` is immutable in a PVC. If you already created the broken PVC, delete the broken objects before applying the fixed file:

```bash
kubectl delete -f scenarios/volumes/02-pvc-wrong-storageclass/broken.yaml --ignore-not-found
kubectl apply -f scenarios/volumes/02-pvc-wrong-storageclass/fixed.yaml
kubectl get pvc -n troubleshooting-lab
```

## 3. Missing Secret Volume

Create the issue:

```bash
kubectl apply -f scenarios/volumes/03-missing-secret-volume/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
ContainerCreating
FailedMount
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=secret-volume-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get secret -n troubleshooting-lab
```

Root cause:

The pod references a Secret named `database-password`, but that Secret does not exist.

Fix:

```bash
kubectl apply -f scenarios/volumes/03-missing-secret-volume/fixed.yaml
kubectl rollout status deploy/secret-volume-demo -n troubleshooting-lab
```

## 4. ConfigMap Key Missing

Create the issue:

```bash
kubectl apply -f scenarios/volumes/04-configmap-key-missing/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=config-key-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get cm app-file-config -n troubleshooting-lab -o yaml
```

Root cause:

The ConfigMap exists, but the pod requests key `config.yaml`. The broken ConfigMap contains `application.yaml`.

Fix:

```bash
kubectl apply -f scenarios/volumes/04-configmap-key-missing/fixed.yaml
kubectl rollout status deploy/config-key-demo -n troubleshooting-lab
```

## 5. Read-Only ConfigMap Write Failure

Create the issue:

```bash
kubectl apply -f scenarios/volumes/05-readonly-configmap-write/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Expected symptom:

```text
CrashLoopBackOff
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=readonly-write-demo -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD" -n troubleshooting-lab
kubectl logs "$POD" --previous -n troubleshooting-lab
kubectl describe pod "$POD" -n troubleshooting-lab
```

Root cause:

ConfigMap volumes are mounted as read-only. The application tries to write into `/etc/app/app.properties`.

Fix:

Copy the config into a writable `emptyDir` and write runtime changes there.

```bash
kubectl apply -f scenarios/volumes/05-readonly-configmap-write/fixed.yaml
kubectl rollout status deploy/readonly-write-demo -n troubleshooting-lab
```

## 6. hostPath Wrong Type

Create the issue:

```bash
kubectl apply -f scenarios/volumes/06-hostpath-wrong-type/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=hostpath-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
```

Root cause:

The pod asks for `hostPath.type: Directory`, but `/this/path/does/not/exist` does not exist on the Kind node.

Fix:

Use `DirectoryOrCreate` for lab/demo use:

```bash
kubectl apply -f scenarios/volumes/06-hostpath-wrong-type/fixed.yaml
kubectl rollout status deploy/hostpath-demo -n troubleshooting-lab
```

Production note:

Avoid `hostPath` for normal application storage. Prefer PVCs. `hostPath` couples the pod to one node.

## 7. emptyDir Data Loss Behavior

This is not exactly a failure. It is important behavior.

Create the demo:

```bash
kubectl apply -f scenarios/volumes/07-emptydir-data-loss/demo.yaml
kubectl rollout status deploy/emptydir-demo -n troubleshooting-lab
POD=$(kubectl get pod -n troubleshooting-lab -l app=emptydir-demo -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n troubleshooting-lab "$POD" -- cat /cache/start-time.txt
```

Delete the pod:

```bash
kubectl delete pod "$POD" -n troubleshooting-lab
kubectl rollout status deploy/emptydir-demo -n troubleshooting-lab
NEW_POD=$(kubectl get pod -n troubleshooting-lab -l app=emptydir-demo -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n troubleshooting-lab "$NEW_POD" -- cat /cache/start-time.txt
```

Observation:

The file exists again, but it has a new timestamp because the new pod got a new `emptyDir`.

Interview line:

`emptyDir` is temporary pod-level storage. It survives container restarts inside the same pod, but it does not survive pod recreation or rescheduling.

