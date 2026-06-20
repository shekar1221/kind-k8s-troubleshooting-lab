$ kubectl get pods -o wide
NAME                              READY   STATUS             RESTARTS      AGE   IP           NODE
       NOMINATED NODE   READINESS GATES
crashloop-demo-54df756f67-2hfj8   0/1     CrashLoopBackOff   8 (81s ago)   17m   10.244.2.5   troubleshooting-worker    <none>           <none>
imagepull-demo-54f7dc4749-68nnx   0/1     ImagePullBackOff   0             18m   10.244.1.6   troubleshooting-worker2   <none>           <none>
netshoot                          1/1     Running            1 (33m ago)   94m   10.244.2.3   troubleshooting-worker    <none>           <none>

##crashloop-demo ###

$ kubectl get events -n troubleshooting-lab --field-selector involvedObject.name=crashloop-demo-54df756f67-2hfj8
LAST SEEN   TYPE      REASON      OBJECT                                MESSAGE
17m         Normal    Scheduled   pod/crashloop-demo-54df756f67-2hfj8   Successfully assigned troubleshooting-lab/crashloop-demo-54df756f67-2hfj8 to troubleshooting-worker
17m         Normal    Pulling     pod/crashloop-demo-54df756f67-2hfj8   Pulling image "busybox:1.36"
17m         Normal    Pulled      pod/crashloop-demo-54df756f67-2hfj8   Successfully pulled image "busybox:1.36" in 4.397s (4.397s including waiting). Image size: 2217006 bytes.
58s         Normal    Created     pod/crashloop-demo-54df756f67-2hfj8   Container created
58s         Normal    Started     pod/crashloop-demo-54df756f67-2hfj8   Container started
58s         Normal    Pulled      pod/crashloop-demo-54df756f67-2hfj8   Container image "busybox:1.36" already present on machine and can be accessed by the pod
55s         Warning   BackOff     pod/crashloop-demo-54df756f67-2hfj8   Back-off restarting failed container app in pod crashloop-demo-54df756f67-2hfj8_troubleshooting-lab(78952438-6fd6-4263-a393-e2e3e67df1b8)

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/pods (main)
$

$ kubectl describe pod crashloop-demo-54df756f67-2hfj8
Name:             crashloop-demo-54df756f67-2hfj8
Namespace:        troubleshooting-lab
Priority:         0
Service Account:  default
Node:             troubleshooting-worker/172.18.0.2
Start Time:       Sat, 20 Jun 2026 19:57:34 +0530
Labels:           app=crashloop-demo
                  pod-template-hash=54df756f67
Annotations:      <none>
Status:           Running
IP:               10.244.2.5
IPs:
  IP:           10.244.2.5
Controlled By:  ReplicaSet/crashloop-demo-54df756f67
Containers:
  app:
    Container ID:  containerd://535c0296e6b51f9a4d4c5213623d124b2170e164aca5373d46600b91cd84e3dd
    Image:         busybox:1.36
    Image ID:      docker.io/library/busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662
    Port:          <none>
    Host Port:     <none>
    Command:
      sh
      -c
    Args:
      echo "Simulating app startup failure"; sleep 2; exit 1
    State:          Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Sat, 20 Jun 2026 20:13:53 +0530
      Finished:     Sat, 20 Jun 2026 20:13:55 +0530
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
      Started:      Sat, 20 Jun 2026 20:08:35 +0530
      Finished:     Sat, 20 Jun 2026 20:08:37 +0530
    Ready:          False
    Restart Count:  8
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-v7b2r (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       False
  ContainersReady             False
  PodScheduled                True
Volumes:
  kube-api-access-v7b2r:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                 From               Message
  ----     ------     ----                ----               -------
  Normal   Scheduled  16m                 default-scheduler  Successfully assigned troubleshooting-lab/crashloop-demo-54df756f67-2hfj8 to troubleshooting-worker
  Normal   Pulling    16m                 kubelet            spec.containers{app}: Pulling image "busybox:1.36"
  Normal   Pulled     16m                 kubelet            spec.containers{app}: Successfully pulled image "busybox:1.36" in 4.397s (4.397s including waiting). Image size: 2217006 bytes.
  Normal   Created    18s (x9 over 16m)   kubelet            spec.containers{app}: Container created
  Normal   Started    18s (x9 over 16m)   kubelet            spec.containers{app}: Container started
  Normal   Pulled     18s (x8 over 16m)   kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Warning  BackOff    15s (x16 over 16m)  kubelet            spec.containers{app}: Back-off restarting failed container app in pod crashloop-demo-54df756f67-2hfj8_troubleshooting-lab(78952438-6fd6-4263-a393-e2e3e67df1b8)


##### fixed crashloop-demo  issue with command echo "Simulating app startup failure"; sleep 2; exit 1### 
 kubectl get pods
NAME                                   READY   STATUS                       RESTARTS      AGE
crashloop-demo-f7ff486fb-xcwrs         1/1     Running                      0             4m4s
imagepull-demo-56dc6df46d-rwx2x        1/1     Running                      0             4m41s
netshoot                               1/1     Running                      1 (46m ago)   106m

 kubectl describe pod crashloop-demo-f7ff486fb-xcwrs
Name:             crashloop-demo-f7ff486fb-xcwrs
Namespace:        troubleshooting-lab
Priority:         0
Service Account:  default
Node:             troubleshooting-worker2/172.18.0.3
Start Time:       Sat, 20 Jun 2026 20:23:22 +0530
Labels:           app=crashloop-demo
                  pod-template-hash=f7ff486fb
Annotations:      <none>
Status:           Running
IP:               10.244.1.8
IPs:
  IP:           10.244.1.8
Controlled By:  ReplicaSet/crashloop-demo-f7ff486fb
Containers:
  app:
    Container ID:  containerd://cc82a169dcc622a7ca0ed5c8d44cb4cadaa2fe03e36a36c060e9380b5408f3dc
    Image:         busybox:1.36
    Image ID:      docker.io/library/busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662
    Port:          <none>
    Host Port:     <none>
    Command:
      sh
      -c
    Args:
      echo "Application is now stable"; sleep 3600
    State:          Running
      Started:      Sat, 20 Jun 2026 20:23:29 +0530
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-tzz8z (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-tzz8z:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Scheduled  2m28s  default-scheduler  Successfully assigned troubleshooting-lab/crashloop-demo-f7ff486fb-xcwrs to troubleshooting-worker2
  Normal  Pulling    2m28s  kubelet            spec.containers{app}: Pulling image "busybox:1.36"
  Normal  Pulled     2m21s  kubelet            spec.containers{app}: Successfully pulled image "busybox:1.36" in 6.776s (6.776s including waiting). Image size: 2217006 bytes.
  Normal  Created    2m21s  kubelet            spec.containers{app}: Container created
  Normal  Started    2m21s  kubelet            spec.containers{app}: Container started


### ImagePullBackOff  ###

$ kubectl describe pod imagepull-demo-54f7dc4749-68nnx |tail
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  22m                   default-scheduler  Successfully assigned troubleshooting-lab/imagepull-demo-54f7dc4749-68nnx to troubleshooting-worker2
  Normal   Pulling    20m (x5 over 22m)     kubelet            spec.containers{app}: Pulling image "nginx:this-tag-does-not-exist"
  Warning  Failed     20m (x5 over 22m)     kubelet            spec.containers{app}: Failed to pull image "nginx:this-tag-does-not-exist": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:this-tag-does-not-exist": failed to resolve reference "docker.io/library/nginx:this-tag-does-not-exist": docker.io/library/nginx:this-tag-does-not-exist: not found
  Warning  Failed     20m (x5 over 22m)     kubelet            spec.containers{app}: Error: ErrImagePull
  Normal   BackOff    2m53s (x84 over 22m)  kubelet            spec.containers{app}: Back-off pulling image "nginx:this-tag-does-not-exist"
  Warning  Failed     2m53s (x84 over 22m)  kubelet            spec.containers{app}: Error: ImagePullBackOff

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/pods (main)
$ kubectl get events --sort-by='.lastTimestamp'  --field-selector involvedObject.name=imagepull-demo-54f7dc4749-68nnx
LAST SEEN   TYPE      REASON      OBJECT                                MESSAGE
23m         Normal    Scheduled   pod/imagepull-demo-54f7dc4749-68nnx   Successfully assigned troubleshooting-lab/imagepull-demo-54f7dc4749-68nnx to troubleshooting-worker2
20m         Normal    Pulling     pod/imagepull-demo-54f7dc4749-68nnx   Pulling image "nginx:this-tag-does-not-exist"
20m         Warning   Failed      pod/imagepull-demo-54f7dc4749-68nnx   Failed to pull image "nginx:this-tag-does-not-exist": rpc error: code = NotFound desc = failed to pull and unpack image "docker.io/library/nginx:this-tag-does-not-exist": failed to resolve reference "docker.io/library/nginx:this-tag-does-not-exist": docker.io/library/nginx:this-tag-does-not-exist: not found
20m         Warning   Failed      pod/imagepull-demo-54f7dc4749-68nnx   Error: ErrImagePull
2m58s       Normal    BackOff     pod/imagepull-demo-54f7dc4749-68nnx   Back-off pulling image "nginx:this-tag-does-not-exist"
2m58s       Warning   Failed      pod/imagepull-demo-54f7dc4749-68nnx   Error: ImagePullBackOff

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/pods (main)
$

#### fixed ImagePullBackOff  wrongly passed image name ###
$ kubectl get pods
NAME                                   READY   STATUS                       RESTARTS      AGE
crashloop-demo-f7ff486fb-xcwrs         1/1     Running                      0             5m51s
imagepull-demo-56dc6df46d-rwx2x        1/1     Running                      0             6m28s
netshoot                               1/1     Running                      1 (47m ago)   108m

$ kubectl describe pod imagepull-demo-56dc6df46d-rwx2x |tail
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Scheduled  5m36s  default-scheduler  Successfully assigned troubleshooting-lab/imagepull-demo-56dc6df46d-rwx2x to troubleshooting-worker2
  Normal  Pulled     5m35s  kubelet            spec.containers{app}: Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
  Normal  Created    5m35s  kubelet            spec.containers{app}: Container created
  Normal  Started    5m35s  kubelet            spec.containers{app}: Container started

### config container error missing --  Environment:          <none> ###

apiVersion: v1
kind: ConfigMap
metadata:
  name: app-runtime-config
  namespace: troubleshooting-lab
data:
  APP_ENV: lab
  FEATURE_FLAG: enabled


$ kubectl get pods
NAME                                   READY   STATUS                       RESTARTS      AGE
missing-config-demo-6f7b87d4c9-r7cmg   0/1     CreateContainerConfigError   0             7m33s
netshoot                               1/1     Running                      1 (51m ago)   112m




$ kubectl describe pod missing-config-demo-6f7b87d4c9-r7cmg
Name:             missing-config-demo-6f7b87d4c9-r7cmg
Namespace:        troubleshooting-lab
Priority:         0
Service Account:  default
Node:             troubleshooting-worker/172.18.0.2
Start Time:       Sat, 20 Jun 2026 20:24:55 +0530
Labels:           app=missing-config-demo
                  pod-template-hash=6f7b87d4c9
Annotations:      <none>
Status:           Pending
IP:               10.244.2.6
IPs:
  IP:           10.244.2.6
Controlled By:  ReplicaSet/missing-config-demo-6f7b87d4c9
Containers:
  app:
    Container ID:
    Image:         busybox:1.36
    Image ID:
    Port:          <none>
    Host Port:     <none>
    Command:
      sh
      -c
      env && sleep 3600
    State:          Waiting
      Reason:       CreateContainerConfigError
    Ready:          False
    Restart Count:  0
    Environment Variables from:
      app-runtime-config  ConfigMap  Optional: false
    Environment:          <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-xk9f5 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       False
  ContainersReady             False
  PodScheduled                True
Volumes:
  kube-api-access-xk9f5:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  6m33s                 default-scheduler  Successfully assigned troubleshooting-lab/missing-config-demo-6f7b87d4c9-r7cmg to troubleshooting-worker
  Normal   Pulled     88s (x26 over 6m32s)  kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Warning  Failed     88s (x26 over 6m32s)  kubelet            spec.containers{app}: Error: configmap "app-runtime-config" not found

$ kubectl get events -n troubleshooting-lab --field-selector involvedObject.name=missing-config-demo-6f7b87d4c9-r7cmg
LAST SEEN   TYPE      REASON      OBJECT                                     MESSAGE
14m         Normal    Scheduled   pod/missing-config-demo-6f7b87d4c9-r7cmg   Successfully assigned troubleshooting-lab/missing-config-demo-6f7b87d4c9-r7cmg to troubleshooting-worker
4m11s       Normal    Pulled      pod/missing-config-demo-6f7b87d4c9-r7cmg   Container image "busybox:1.36" already present on machine and can be accessed by the pod
4m11s       Warning   Failed      pod/missing-config-demo-6f7b87d4c9-r7cmg   Error: configmap "app-runtime-config" not found


## fixed the missing configuration on pod ###

$ kubectl get pods
NAME                                   READY   STATUS    RESTARTS      AGE
missing-config-demo-6f7b87d4c9-r7cmg   1/1     Running   0             16m
netshoot                               1/1     Running   1 (59m ago)   120m



$ kubectl logs missing-config-demo-6f7b87d4c9-r7cmg
KUBERNETES_SERVICE_PORT=443
KUBERNETES_PORT=tcp://10.96.0.1:443
ORDERS_API_SERVICE_PORT=80
ORDERS_API_PORT=tcp://10.96.93.164:80
HOSTNAME=missing-config-demo-6f7b87d4c9-r7cmg
SHLVL=1
HOME=/root
ORDERS_API_PORT_80_TCP_ADDR=10.96.93.164
ORDERS_API_PORT_80_TCP_PORT=80
ORDERS_API_PORT_80_TCP_PROTO=tcp
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ORDERS_API_PORT_80_TCP=tcp://10.96.93.164:80
KUBERNETES_PORT_443_TCP_PORT=443
KUBERNETES_PORT_443_TCP_PROTO=tcp
ORDERS_API_SERVICE_PORT_HTTP=80
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
KUBERNETES_SERVICE_PORT_HTTPS=443
FEATURE_FLAG=enabled
APP_ENV=lab
KUBERNETES_SERVICE_HOST=10.96.0.1
PWD=/
ORDERS_API_SERVICE_HOST=10.96.93.164

$ kubectl describe pod missing-config-demo-6f7b87d4c9-r7cmg
Name:             missing-config-demo-6f7b87d4c9-r7cmg
Namespace:        troubleshooting-lab
Priority:         0
Service Account:  default
Node:             troubleshooting-worker/172.18.0.2
Start Time:       Sat, 20 Jun 2026 20:24:55 +0530
Labels:           app=missing-config-demo
                  pod-template-hash=6f7b87d4c9
Annotations:      <none>
Status:           Running
IP:               10.244.2.6
IPs:
  IP:           10.244.2.6
Controlled By:  ReplicaSet/missing-config-demo-6f7b87d4c9
Containers:
  app:
    Container ID:  containerd://0fd99b175bb7d4b773b368d1cdd3fb0aed32be796da0ddb26c1b7960294d0750
    Image:         busybox:1.36
    Image ID:      docker.io/library/busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662
    Port:          <none>
    Host Port:     <none>
    Command:
      sh
      -c
      env && sleep 3600
    State:          Running
      Started:      Sat, 20 Jun 2026 20:39:46 +0530
    Ready:          True
    Restart Count:  0
    Environment Variables from:
      app-runtime-config  ConfigMap  Optional: false
    Environment:          <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-xk9f5 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-xk9f5:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  17m                   default-scheduler  Successfully assigned troubleshooting-lab/missing-config-demo-6f7b87d4c9-r7cmg to troubleshooting-worker
  Normal   Pulled     7m27s (x49 over 17m)  kubelet            spec.containers{app}: Container image "busybox:1.36" already present on machine and can be accessed by the pod
  Warning  Failed     7m27s (x49 over 17m)  kubelet            spec.containers{app}: Error: configmap "app-runtime-config" not found




#####  READINESS probe failed with 404 ####

$ kubectl get deployments readiness-demo
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
readiness-demo   0/2     2            0           6m3s


$ kubectl get pods |grep -i readiness-demo
readiness-demo-84ffb7f8-4xpk2          0/1     Running   0             6m22s
readiness-demo-84ffb7f8-jh9r7          0/1     Running   0             6m22s

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/pods/03-createcontainerconfigerror (main)
$

##### fixed readiness-demo  *** 

$ kubectl describe deployment.apps/readiness-demo
Name:                   readiness-demo
Namespace:              troubleshooting-lab
CreationTimestamp:      Sat, 20 Jun 2026 20:45:16 +0530
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 2
Selector:               app=readiness-demo
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=readiness-demo
  Containers:
   app:
    Image:         nginx:1.27-alpine
    Port:          80/TCP
    Host Port:     0/TCP
    Readiness:     http-get http://:80/ delay=3s timeout=1s period=5s #success=1 #failure=3
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  readiness-demo-84ffb7f8 (0/0 replicas created)
NewReplicaSet:   readiness-demo-5cbcd47557 (2/2 replicas created)
Events:
  Type    Reason             Age    From                   Message
  ----    ------             ----   ----                   -------
  Normal  ScalingReplicaSet  7m10s  deployment-controller  Scaled up replica set readiness-demo-84ffb7f8 from 0 to 2
  Normal  ScalingReplicaSet  24s    deployment-controller  Scaled up replica set readiness-demo-5cbcd47557 from 0 to 1
  Normal  ScalingReplicaSet  18s    deployment-controller  Scaled down replica set readiness-demo-84ffb7f8 from 2 to 1
  Normal  ScalingReplicaSet  18s    deployment-controller  Scaled up replica set readiness-demo-5cbcd47557 from 1 to 2
  Normal  ScalingReplicaSet  12s    deployment-controller  Scaled down replica set readiness-demo-84ffb7f8 from 1 to 0




$ kubectl get events -n troubleshooting-lab --field-selector involvedObject.name=readiness-demo-84ffb7f8-jh9r7
LAST SEEN   TYPE      REASON      OBJECT                              MESSAGE
4m57s       Normal    Scheduled   pod/readiness-demo-84ffb7f8-jh9r7   Successfully assigned troubleshooting-lab/readiness-demo-84ffb7f8-jh9r7 to troubleshooting-worker
4m57s       Normal    Pulled      pod/readiness-demo-84ffb7f8-jh9r7   Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
4m56s       Normal    Created     pod/readiness-demo-84ffb7f8-jh9r7   Container created
4m56s       Normal    Started     pod/readiness-demo-84ffb7f8-jh9r7   Container started
2m52s       Warning   Unhealthy   pod/readiness-demo-84ffb7f8-jh9r7   Readiness probe failed: HTTP probe failed with statuscode: 404


$ kubectl describe  pod/readiness-demo-84ffb7f8-4xpk2
Name:             readiness-demo-84ffb7f8-4xpk2
Namespace:        troubleshooting-lab
Priority:         0
Service Account:  default
Node:             troubleshooting-worker2/172.18.0.3
Start Time:       Sat, 20 Jun 2026 20:45:16 +0530
Labels:           app=readiness-demo
                  pod-template-hash=84ffb7f8
Annotations:      <none>
Status:           Running
IP:               10.244.1.9
IPs:
  IP:           10.244.1.9
Controlled By:  ReplicaSet/readiness-demo-84ffb7f8
Containers:
  app:
    Container ID:   containerd://a55cdbd1988aeff2c9b070cb5fe15e89cd5c4d3c96429b5640afa728a7c7304c
    Image:          nginx:1.27-alpine
    Image ID:       docker.io/library/nginx@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10
    Port:           80/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Sat, 20 Jun 2026 20:45:17 +0530
    Ready:          False
    Restart Count:  0
    Readiness:      http-get http://:80/missing-health-page delay=3s timeout=1s period=5s #success=1 #failure=3
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-psvj7 (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       False
  ContainersReady             False
  PodScheduled                True
Volumes:
  kube-api-access-psvj7:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  2m54s                 default-scheduler  Successfully assigned troubleshooting-lab/readiness-demo-84ffb7f8-4xpk2 to troubleshooting-worker2
  Normal   Pulled     2m54s                 kubelet            spec.containers{app}: Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
  Normal   Created    2m53s                 kubelet            spec.containers{app}: Container created
  Normal   Started    2m53s                 kubelet            spec.containers{app}: Container started
  Warning  Unhealthy  51s (x25 over 2m48s)  kubelet            spec.containers{app}: Readiness probe failed: HTTP probe failed with statuscode: 404

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/deployments/01-readiness-rollout-stuck (main)
$
$ kubectl get events -n troubleshooting-lab --field-selector involvedObject.name=readiness-demo-5cbcd47557-fbsqm
LAST SEEN   TYPE     REASON      OBJECT                                MESSAGE
3m15s       Normal   Scheduled   pod/readiness-demo-5cbcd47557-fbsqm   Successfully assigned troubleshooting-lab/readiness-demo-5cbcd47557-fbsqm to troubleshooting-worker2
3m14s       Normal   Pulled      pod/readiness-demo-5cbcd47557-fbsqm   Container image "nginx:1.27-alpine" already present on machine and can be accessed by the pod
3m14s       Normal   Created     pod/readiness-demo-5cbcd47557-fbsqm   Container created
3m14s       Normal   Started     pod/readiness-demo-5cbcd47557-fbsqm   Container started

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab/scenarios/deployments/01-readiness-rollout-stuck (main)
$ kubectl get events -n troubleshooting-lab --field-selector involvedObject.name=readiness-demo
LAST SEEN   TYPE     REASON              OBJECT                      MESSAGE
10m         Normal   ScalingReplicaSet   deployment/readiness-demo   Scaled up replica set readiness-demo-84ffb7f8 from 0 to 2
3m22s       Normal   ScalingReplicaSet   deployment/readiness-demo   Scaled up replica set readiness-demo-5cbcd47557 from 0 to 1
3m16s       Normal   ScalingReplicaSet   deployment/readiness-demo   Scaled down replica set readiness-demo-84ffb7f8 from 2 to 1
3m16s       Normal   ScalingReplicaSet   deployment/readiness-demo   Scaled up replica set readiness-demo-5cbcd47557 from 1 to 2
3m10s       Normal   ScalingReplicaSet   deployment/readiness-demo   Scaled down replica set readiness-demo-84ffb7f8 from 1 to 0

