#!/bin/bash

set -ex

function run_docker_compose() {

# Substitute docker image variable
export IMAGE_NAME='${AWS_ECR_ID}/${CIRCLE_BRANCH}-${PROJECT_NAME}:TAG'
sed -i "s@IMAGE_NAME@${IMAGE_NAME}@" docker-compose.yml

# Pull environment variables
aws secretsmanager get-secret-value --secret-id "${CIRCLE_BRANCH}/${PROJECT_NAME}/backend" --region $AWS_DEFAULT_REGION | \
    jq -r '.SecretString' | \
    jq -r "to_entries|map(\"\(.key)=\\\"\(.value|tostring)\\\"\")|.[]"| \
    sed -e 's/"//' -e 's/"$//' > .env

# Login to ECR    
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ECR_ID

# Start docker-compose
docker-compose up -d
}

# Add ip of the container to RDS security group
function add_ip_to_rds_sg() {
    export public_ip_address=$(docker exec -u 0 backend sh -c 'wget -qO- http://checkip.amazonaws.com');
    aws ec2 authorize-security-group-ingress --region "${AWS_DEFAULT_REGION}" --group-id "${AWS_RDS_SG_ID}" --protocol tcp --port 5432 --cidr "$public_ip_address"/32
}

# Rails command ouputs result "up" means the migration has been run and "down" means that we need to run the migration. 
function check_migrations () {
if [ "$(docker exec backend sh -c 'rails db:migrate:status | grep -c "^\s*down"')" == "0" ]; then   #####
    export run_migrations=false
else
    export run_migrations=true
fi
}

# Delete ip from the container to RDS security group
function delete_ip_from_rds_sg() {
    export public_ip_address=$(docker exec -u 0 backend sh -c 'wget -qO- http://checkip.amazonaws.com');
    aws ec2 revoke-security-group-ingress --region "${AWS_DEFAULT_REGION}" --group-id "${AWS_RDS_SG_ID}" --protocol tcp --port 5432 --cidr "$public_ip_address"/32
}

#Delete old snapshots
function delete_old_snapshot() {
    local snapshots_list=$(aws rds describe-db-snapshots --snapshot-type 'manual' --db-instance-identifier "${CIRCLE_BRANCH}-${PROJECT_NAME}" --region "${AWS_DEFAULT_REGION}" | jq '.DBSnapshots[]' | jq -r '.DBSnapshotIdentifier' | awk /\d/ | head )
    local snapshot
    for snapshot in ${snapshots_list}; do
        aws rds delete-db-snapshot --db-snapshot-identifier "${snapshot}" --region "${AWS_DEFAULT_REGION}"
        echo "Deleting snapshot ${snapshot}"
    done
}
#Create new snapshot
function create_new_snapshots() {
    export snapshot_name="${CIRCLE_BRANCH}-${PROJECT_NAME}-deploy-${CIRCLE_SHA1}"
    aws rds create-db-snapshot --db-instance-identifier "${CIRCLE_BRANCH}-${PROJECT_NAME}" --db-snapshot-identifier "${snapshot_name}" --tags "Key=Source,Value=Deployment" --region "${AWS_DEFAULT_REGION}"
    echo "Waiting for ${snapshot_name} snapshot creation"
    aws rds wait db-snapshot-completed --db-snapshot-identifier "${snapshot_name}" --region "${AWS_DEFAULT_REGION}"
}

function run_migrations() {
docker exec -u 0 backend sh -c 'bin/rails db:migrate' #####
}

function main() {
    run_docker_compose
    add_ip_to_rds_sg
    check_migrations
    
# if [ "$run_migrations" == "true" ]; then
    delete_old_snapshot
    create_new_snapshots
    run_migrations
    delete_ip_from_rds_sg
# else
#     delete_ip_from_rds_sg
# fi
}

main "$@" || (delete_ip_from_rds_sg && exit 1)
