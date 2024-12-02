from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret
from kubernetes.client import models as k8s


secret_opensearch = [Secret(
    deploy_type="env",
    deploy_target=key,
    secret="opensearch-conn"
)
    for key in ["OPTION_DB_VECTOR", "HOST_DB_VECTOR", "INDEX_FORMATION"]
]

volume = k8s.V1Volume(
    name="data-folder",
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
        claim_name="data-folder"
    )
)

volume_mount = k8s.V1VolumeMount(
    name="data-folder",
    mount_path="/app/data/to_ingest"
)

env_dict = {"DATE_FOLDER": "{{ logical_date | ds }}"}


with DAG(
    dag_id='ETL',
    tags=['ETL', 'contact-prof'],
    default_args={
        'owner': 'romain'
    },
    schedule_interval=None,
    catchup=False
) as dag:

    extract_features = KubernetesPodOperator(
        namespace="airflow",
        task_id="clean-transform-data",
        image="leutergmail/transform-data-formation",
        cmds=["python3", "main.py"],
        on_finish_action="delete_pod",
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_vars=env_dict
    )

    send_to_database = KubernetesPodOperator(
        namespace="airflow",
        task_id="send-to-opensearch",
        image="leutergmail/load-data-formation",
        cmds=["python3", "main.py"],
        secrets=secret_opensearch,
        volumes=[volume],
        volume_mounts=[volume_mount],
        on_finish_action="delete_pod",
        env_vars=env_dict
    )

extract_features >> send_to_database
