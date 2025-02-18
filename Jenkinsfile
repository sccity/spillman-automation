pipeline {
    agent {
        kubernetes {
            label "${env.JOB_NAME}-${BUILD_NUMBER}"
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: jnlp
      image: sccity/jenkins-agent-python:0.0.4
      volumeMounts:
        - name: workspace-volume
          mountPath: /home/jenkins/agent

    - name: docker
      image: docker:24.0.6-dind
      securityContext:
        privileged: true
      command: ["dockerd-entrypoint.sh"]
      args: ["--host=tcp://0.0.0.0:2375", "--host=unix:///var/run/docker.sock"]
      volumeMounts:
        - name: docker-lib
          mountPath: /var/lib/docker

  volumes:
    - name: workspace-volume
      emptyDir: {}

    - name: docker-lib
      emptyDir: {}
            '''
        }
    }

    stages {
        stage('Database') {
            steps {
                container('jnlp') {
                    sh '''
                    echo "development" | su -c "/etc/init.d/mariadb start" root
                    until mysqladmin ping --silent; do sleep 3; done
                    echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '';" > setup.sql
                    echo "FLUSH PRIVILEGES;" >> setup.sql
                    echo "CREATE DATABASE spillman_automation;" >> setup.sql
                    echo "development" | su -c "mysql -u root < setup.sql" root
                    '''
                }
            }
        }

        stage('Build') {
            steps {
                container('jnlp') {
                    sh '''
                    python3.10 -m venv venv
                    . venv/bin/activate
                    pip3.10 install -r requirements.txt
                    cp .env.example .env
                    sed -i 's/^DB_HOST=.*/DB_HOST=localhost/' .env
                    sed -i 's/^DB_HOST_RO=.*/DB_HOST_RO=localhost/' .env
                    sed -i 's/^DB_SCHEMA=.*/DB_SCHEMA=spillman_automation/' .env
                    sed -i 's/^DB_USER=.*/DB_USER=root/' .env
                    sed -i 's/^DB_PASSWORD=.*/DB_PASSWORD=/' .env
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('jnlp') {
                    sh '''
                    . venv/bin/activate
                    python3.10 app.py --check-config
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                container('jnlp') {
                    withCredentials([usernamePassword(credentialsId: 'git', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                        sh '''
                        commit_hash=$(date +"%Y%m%d%H%M%S")_$(git rev-parse --short HEAD)
                        branch=$(git rev-parse --abbrev-ref HEAD || echo "detached")
                        echo "Branch: ${branch} - Commit Hash: $commit_hash"

                        git config --global user.email "jenkins@email.santaclarautah.gov"
                        git config --global user.name "Jenkins"

                        if git ls-remote --tags origin | grep -q "refs/tags/$commit_hash"; then
                            echo "Tag $commit_hash already exists. Skipping tag creation."
                        else
                            echo "Creating and pushing Git tag: $commit_hash"

                            GIT_ASKPASS=$(mktemp)
                            echo '#!/bin/sh' > $GIT_ASKPASS
                            echo 'echo "$GIT_PASSWORD"' >> $GIT_ASKPASS
                            chmod +x $GIT_ASKPASS

                            git tag -a "$commit_hash" -m "Automated Build $commit_hash"
                            GIT_ASKPASS=$GIT_ASKPASS git push origin tag "$commit_hash"

                            rm -f $GIT_ASKPASS
                        fi

                        echo $commit_hash > commit_hash.txt
                        '''
                    }
                }

                container('docker') {
                    sh '''
                    commit_hash=$(cat commit_hash.txt)
                    if [ -z "$commit_hash" ]; then
                        echo "Error: Commit hash file is missing!"
                        exit 1
                    fi

                    echo "Using Commit Hash: $commit_hash for Docker build"
                    chmod +x build.sh
                    ./build.sh $commit_hash
                    '''
                }
            }
        }
        fixed {
            script {
                def logLines = currentBuild.rawBuild.getLog(100).join('\n')
                emailext(
                    to: 'lhaynie@santaclarautah.gov, rlevsey@santaclarautah.gov',
                    subject: "Build Fixed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        <strong>Project:</strong> ${env.JOB_NAME}<br>
                        <strong>Build Number:</strong> ${env.BUILD_NUMBER}<br>
                        <strong>Result:</strong> ${currentBuild.currentResult}<br>
                        <strong>URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br><br>
                        <strong>Last 100 lines of build log:</strong>
                        <pre>${logLines}</pre>
                        """,
                    mimeType: 'text/html'
                )
            }
        }
        failure {
            script {
                def logLines = currentBuild.rawBuild.getLog(100).join('\n')
                emailext(
                    to: 'lhaynie@santaclarautah.gov, rlevsey@santaclarautah.gov',
                    subject: "Build Failed: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        <strong>Project:</strong> ${env.JOB_NAME}<br>
                        <strong>Build Number:</strong> ${env.BUILD_NUMBER}<br>
                        <strong>Result:</strong> ${currentBuild.currentResult}<br>
                        <strong>URL:</strong> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a><br><br>
                        <strong>Last 100 lines of build log:</strong>
                        <pre>${logLines}</pre>
                        """,
                    mimeType: 'text/html'
                )
            }
        }
    }
}
