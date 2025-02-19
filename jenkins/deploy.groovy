withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
    sh '''
    commit_hash=$(cat commit_hash.txt)
    branch=$(cat branch.txt)

    namespace="spillman"
    container="spillman-automation"
    image="sccity/spillman-automation"

    if [ "$branch" = "dev" ]; then
        exit 0
    elif [ "$branch" = "prod" ]; then
        STATEFULSET="spillman-automation"
    else
        echo "Error: Unknown branch '$branch'. Skipping statefulset."
        exit 1
    fi

    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl

    ./kubectl get statefulsets -n $namespace

    tmp1="{\"spec\":{\"template\":{\"spec\":"
    tmp2="{\"containers\": [{\"name\": \"$container\", \"image\": \"$commit_hash-$branch\"}]}}}"
    echo $tmp1$tmp2 > tmp.json

    ./kubectl patch statefulset $STATEFULSET --patch-file tmp.json -n $namespace

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes Update Failed!"
        exit 1
    fi

    ./kubectl -n $namespace \
        rollout status statefulset/$STATEFULSET \
        -n $namespace

    if [ $? -ne 0 ]; then
        echo "Error: Kubernetes Rollout Failed!"
        exit 1
    fi
    '''
}