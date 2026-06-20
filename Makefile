CLUSTER_NAME := troubleshooting
NAMESPACE := troubleshooting-lab

.PHONY: create-cluster delete-cluster base status events

create-cluster:
	kind create cluster --config kind/cluster-2-workers.yaml

delete-cluster:
	kind delete cluster --name $(CLUSTER_NAME)

base:
	kubectl apply -f manifests/base/

status:
	kubectl get nodes -o wide
	kubectl get all -n $(NAMESPACE)

events:
	kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

