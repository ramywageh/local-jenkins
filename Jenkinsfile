pipeline {
    agent any

    parameters {
        booleanParam(name: 'autoApprove', defaultValue: false, description: 'Automatically run apply after generating plan?')
        choice(name: 'action', choices: ['apply', 'destroy'], description: 'Select the action to perform')
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        AWS_DEFAULT_REGION    = 'ap-south-1'
        TERRAFORM_VERSION = "1.9.2"
        TERRAFORM_BIN_DIR = "${WORKSPACE}/terraform-bin"
        TERRAFORM_DIR = "Terraform/"
    }
    

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ramywageh/local-jenkins.git'
            }
        }
        stage('Install Terraform') {
            steps {
                script {
                    sh '''
                        set -e

                        echo "Creating local bin directory..."
                        mkdir -p ${TERRAFORM_BIN_DIR}
                        cd /tmp

                        echo "Downloading Terraform ${TERRAFORM_VERSION}..."
                        curl -s -O https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip

                        echo "Unzipping..."
                        unzip -o terraform_${TERRAFORM_VERSION}_linux_amd64.zip

                        echo "Moving Terraform binary to local bin dir..."
                        mv terraform ${TERRAFORM_BIN_DIR}/terraform

                        echo "Cleaning up..."
                        rm -f terraform_${TERRAFORM_VERSION}_linux_amd64.zip
                    '''
                }
            }
        }
        stage('Terraform Init') {
            steps {
                withEnv(["PATH=${env.TERRAFORM_BIN_DIR}:/usr/bin:/bin"]) {
                    dir("${TERRAFORM_DIR}") {
                        sh '''
                          terraform version
                          terraform init
                        '''
                    }    
                }
            }
        }
        stage('Plan') {
            steps {
                withEnv(["PATH=${TERRAFORM_BIN_DIR}:${env.PATH}"]) {
                   dir("${TERRAFORM_DIR}") { 
                      sh 'terraform plan -out tfplan'
                      sh 'terraform show -no-color tfplan > tfplan.txt'
                    } 
                }
            }
        }
        stage('Apply / Destroy') {
            steps {
                withEnv(["PATH=${TERRAFORM_BIN_DIR}:${env.PATH}"]) {
                    dir("${TERRAFORM_DIR}") { 
                        script {
                            if (params.action == 'apply') {
                                if (!params.autoApprove) {
                                 def plan = readFile 'tfplan.txt'
                                 input message: "Do you want to apply the plan?",
                                 parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                                }
              
                            sh 'terraform ${action} -input=false tfplan'
                            } else if (params.action == 'destroy') {
                                sh 'terraform ${action} --auto-approve'
                            } else {
                                error "Invalid action selected. Please choose either 'apply' or 'destroy'."
                            }
                        }
                    }
                }
            }
        }
        stage('Build') {
            steps {
                // Create necessary directories and files if they don't exist
                sh 'mkdir -p templates'
                sh 'echo "Flask==2.0.1\nprometheus_flask_exporter==0.18.7\ngunicorn==20.1.0" > requirements.txt'
                sh 'echo "<!DOCTYPE html><html><head><title>Todo App</title></head><body><h1>Todo List</h1><form action=\'/add\' method=\'post\'><input type=\'text\' name=\'task\'><input type=\'submit\' value=\'Add Task\'></form><ul>{% for task in tasks %}<li>{{ task }} <a href=\'/delete/{{ loop.index0 }}\'>Delete</a></li>{% endfor %}</ul></body></html>" > templates/index.html'
                
                // Build Docker image
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                
                // Optional: Push to Docker registry if needed
                // Make sure to set up Docker registry credentials in Jenkins
                // withCredentials([string(credentialsId: 'docker-registry-credentials', variable: 'DOCKER_PASSWORD')]) {
                //     sh "echo ${DOCKER_PASSWORD} | docker login -u username --password-stdin"
                //     sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                //     sh "docker push ${DOCKER_IMAGE}:latest"
                // }
            }
        }
    }
}