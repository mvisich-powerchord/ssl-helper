#!/bin/bash
set -euo pipefail
set -x

kubectl apply -f namespace.yaml

kubectl apply -f service-account.yaml -n k8s-ssl-updater

kubectl apply -f role.yaml
kubectl apply -f role-binding.yaml

kubectl apply -f deployment.yaml -n k8s-ssl-updater

kubectl apply -f service.yaml -n k8s-ssl-updater
