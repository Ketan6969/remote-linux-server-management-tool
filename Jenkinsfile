pipeline {
    agent any 
    environment {
        DOCKER_CREDENTIAL_ID = 'docker-hub-credentials'
        REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'ketan2004/remote-linux-server-management-tool' 
        }

    stages {
        stage('checkout') {
            steps {
                // This will fetch the code from GitHub
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/Ketan6969/remote-linux-server-management-tool.git']]])
            }
        }

        stage('docker-build') {
            steps {
                script {
                    echo "Building the docker image...."
                    docker.build("${DOCKER_IMAGE}:latest")
                    echo "Docker image build success!!"
                }
            }
        }  
        
        stage('docker-push') {
            steps {
                script {
                    echo "Executing the docker push stage"
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIAL_ID}", usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        sh '''
                            echo "$PASSWORD" | docker login -u "$USERNAME" --password-stdin
                            docker push ${DOCKER_IMAGE}:latest
                        '''
                    }
                    echo "Docker push complete!!"
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
