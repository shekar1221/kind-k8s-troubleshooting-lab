# Test Scenarios With Commands

Use this document as your hands-on practice sheet. Run one scenario at a time.

## 0. Start Lab

```bash
cd kind-k8s-troubleshooting-lab
kind create cluster --config kind/cluster-2-workers.yaml
kubectl apply -f manifests/base/
kubectl get nodes -o wide
kubectl get pods -n troubleshooting-lab
```

Expected:

```text
orders-api pods are Running
netshoot is Running
health-checker is Running
```

## 1. Baseline Health Check

Run inside the cluster:

```bash
kubectl exec -n troubleshooting-lab health-checker -- python /scripts/health_check.py
```

At the beginning, some checks can fail because not all scenario services are created yet. After you fix each scenario, run the same command again.

Run from laptop for NodePort/localhost tests:

```bash
python scripts/health_check.py --target local-orders-api:localhost:8080:/
```

## 2. Pod Scenario: ImagePullBackOff

Create failure:

```bash
kubectl apply -f scenarios/pods/01-imagepullbackoff/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=imagepull-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get events -n troubleshooting-lab --sort-by='.lastTimestamp'
```

What to observe:

```text
Failed to pull image
ErrImagePull
ImagePullBackOff
```

Fix:

```bash
kubectl apply -f scenarios/pods/01-imagepullbackoff/fixed.yaml
kubectl rollout status deploy/imagepull-demo -n troubleshooting-lab
```

Validate:

```bash
kubectl get pods -n troubleshooting-lab -l app=imagepull-demo
```

## 3. Pod Scenario: CrashLoopBackOff

Create failure:

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

What to observe:

```text
Back-off restarting failed container
Container exits with error
```

Fix:

```bash
kubectl apply -f scenarios/pods/02-crashloopbackoff/fixed.yaml
kubectl rollout status deploy/crashloop-demo -n troubleshooting-lab
```

## 4. Deployment Scenario: Readiness Probe Failure

Create failure:

```bash
kubectl apply -f scenarios/deployments/01-readiness-rollout-stuck/broken.yaml
kubectl get deploy,pods -n troubleshooting-lab -l app=readiness-demo
```

Troubleshoot:

```bash
kubectl rollout status deploy/readiness-demo -n troubleshooting-lab
kubectl describe deploy readiness-demo -n troubleshooting-lab
POD=$(kubectl get pod -n troubleshooting-lab -l app=readiness-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
```

What to observe:

```text
Readiness probe failed
HTTP probe failed with statuscode: 404
```

Fix:

```bash
kubectl apply -f scenarios/deployments/01-readiness-rollout-stuck/fixed.yaml
kubectl rollout status deploy/readiness-demo -n troubleshooting-lab
```

## 5. Service Scenario: Empty Endpoints

Create failure:

```bash
kubectl apply -f scenarios/networking/01-service-selector-mismatch/broken.yaml
kubectl get svc,endpoints -n troubleshooting-lab
```

Troubleshoot:

```bash
kubectl describe svc selector-backend -n troubleshooting-lab
kubectl get endpoints selector-backend -n troubleshooting-lab
kubectl get pods -n troubleshooting-lab --show-labels
kubectl exec -n troubleshooting-lab netshoot -- curl -v http://selector-backend.troubleshooting-lab.svc.cluster.local
```

What to observe:

```text
Endpoints: <none>
Service selector app=selector-backend-wrong
Pod label app=selector-backend
```

Fix:

```bash
kubectl apply -f scenarios/networking/01-service-selector-mismatch/fixed.yaml
kubectl get endpoints selector-backend -n troubleshooting-lab
kubectl exec -n troubleshooting-lab netshoot -- curl -s http://selector-backend.troubleshooting-lab.svc.cluster.local
kubectl exec -n troubleshooting-lab health-checker -- python /scripts/health_check.py
```

## 6. Network Scenario: Wrong targetPort

Create failure:

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
kubectl logs "$POD" -n troubleshooting-lab
```

What to observe:

```text
Endpoints exist, but curl fails
Application listens on 8080
Service targetPort is 9090
```

Fix:

```bash
kubectl apply -f scenarios/networking/02-wrong-targetport/fixed.yaml
kubectl exec -n troubleshooting-lab netshoot -- curl -s http://targetport-api.troubleshooting-lab.svc.cluster.local
kubectl exec -n troubleshooting-lab health-checker -- python /scripts/health_check.py
```

## 7. Init Container Scenario

Create failure:

```bash
kubectl apply -f scenarios/init-containers/01-init-waiting-for-service/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=init-wait-demo -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD" -c wait-for-db -n troubleshooting-lab
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get svc -n troubleshooting-lab
```

What to observe:

```text
waiting for payments-db
DNS lookup fails because service is missing
```

Fix:

```bash
kubectl apply -f scenarios/init-containers/01-init-waiting-for-service/fixed.yaml
kubectl rollout status deploy/payments-db -n troubleshooting-lab
kubectl rollout status deploy/init-wait-demo -n troubleshooting-lab
kubectl exec -n troubleshooting-lab health-checker -- python /scripts/health_check.py
```

## 8. Volume Scenario: Missing ConfigMap Volume

Create failure:

```bash
kubectl apply -f scenarios/volumes/01-missing-configmap-volume/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=volume-config-demo -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
kubectl get cm -n troubleshooting-lab
```

What to observe:

```text
MountVolume.SetUp failed
configmap "nginx-custom-config" not found
```

Fix:

```bash
kubectl apply -f scenarios/volumes/01-missing-configmap-volume/fixed.yaml
kubectl rollout status deploy/volume-config-demo -n troubleshooting-lab
```

## 9. Volume Scenario: PVC Wrong StorageClass

Create failure:

```bash
kubectl apply -f scenarios/volumes/02-pvc-wrong-storageclass/broken.yaml
kubectl get pvc,pods -n troubleshooting-lab
```

Troubleshoot:

```bash
kubectl describe pvc reports-pvc -n troubleshooting-lab
kubectl get storageclass
POD=$(kubectl get pod -n troubleshooting-lab -l app=reports-api -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod "$POD" -n troubleshooting-lab
```

What to observe:

```text
PVC Pending
storageclass.storage.k8s.io "gold-storage-does-not-exist" not found
```

Fix:

```bash
kubectl delete -f scenarios/volumes/02-pvc-wrong-storageclass/broken.yaml --ignore-not-found
kubectl apply -f scenarios/volumes/02-pvc-wrong-storageclass/fixed.yaml
kubectl get pvc -n troubleshooting-lab
kubectl rollout status deploy/reports-api -n troubleshooting-lab
```

## 10. Volume Scenario: Read-Only ConfigMap Write

Create failure:

```bash
kubectl apply -f scenarios/volumes/05-readonly-configmap-write/broken.yaml
kubectl get pods -n troubleshooting-lab
```

Troubleshoot:

```bash
POD=$(kubectl get pod -n troubleshooting-lab -l app=readonly-write-demo -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD" --previous -n troubleshooting-lab
kubectl describe pod "$POD" -n troubleshooting-lab
```

What to observe:

```text
Read-only file system
Back-off restarting failed container
```

Fix:

```bash
kubectl apply -f scenarios/volumes/05-readonly-configmap-write/fixed.yaml
kubectl rollout status deploy/readonly-write-demo -n troubleshooting-lab
```

## 11. Scheduling Scenario: Node Selector Mismatch

Create failure:

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

What to observe:

```text
0/3 nodes are available
node(s) didn't match Pod's node affinity/selector
```

Fix:

```bash
kubectl apply -f scenarios/scheduling/01-node-selector-mismatch/fixed.yaml
kubectl rollout status deploy/node-selector-demo -n troubleshooting-lab
```

Alternative fix by labeling a worker:

```bash
kubectl label node troubleshooting-worker disktype=ssd
kubectl get pods -n troubleshooting-lab -o wide
```

## 12. Cleanup

Delete the whole Kind cluster:

```bash
kind delete cluster --name troubleshooting
```

