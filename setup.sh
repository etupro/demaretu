## Installation of database
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install scrapping bitnami/postgresql -f /home/romain/Documents/EduPro/scrapping/kubernetes/custom_values.yaml -n scrap --create-namespace
