# helm uninstall airflow -n airflow
# kubectl delete pvc --all -n airflow
# kubectl delete pv --all -n airflow

if [! -d "./src/provider/logs"]; then
mkdir -p ./src/provider/logs ;
fi

kubectl create namespace airflow
helm repo add apache-airflow https://airflow.apache.org
helm update

# TODO: 
# kubectl create secret generic mydatabase --from-literal=connection=postgresql://admin:admin@10.43.150.34:5432/postgres

## Log / dag / data folder 
kubectl apply -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pv-pvc.yaml
kubectl apply -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pv-pvc.yaml

## Env for DAG
kubectl apply -f ./src/provider/kubernetes/dag_env/data-folder-pv-pvc.yaml
kubectl apply -f ./src/provider/kubernetes/dag_env/opensearch-conn-secret.yaml

# update helm
helm install airflow apache-airflow/airflow -f ./src/provider/kubernetes/installation/custom.yaml -n airflow --debug
