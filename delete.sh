kubectl delete -f service.yaml -n k8s-ssl-updater
kubectl delete -f deployment.yaml -n k8s-ssl-updater
kubectl delete -f role-binding.yaml
kubectl delete -f role.yaml
kubectl delete -f service-account.yaml -n k8s-ssl-updater
kubectl delete -f namespace.yaml
