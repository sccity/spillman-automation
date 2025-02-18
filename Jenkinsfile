pipeline {
    agent {
        kubernetes {
            label "${env.JOB_NAME}-${BUILD_NUMBER}"
            containerTemplate {
                name 'jnlp'
                image 'sccity/jenkins-agent-python:0.0.3'
            }
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
                withCredentials([usernamePassword(credentialsId: 'git', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh '''
                    hash=$(git rev-parse HEAD | head -c 7)
                    echo "Commit Hash: $hash"
                    git tag -a "$commit_hash" -m "Automated Build ${commit_hash}"
                    git push origin ${env.BRANCH_NAME}:refs/tags/$commit_hash
                    '''
                }
            }
        }
        failure {
            script {
                def logLines = currentBuild.rawBuild.getLog(100).join("\n")
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
