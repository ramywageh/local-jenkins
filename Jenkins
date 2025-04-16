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
                git branch: 'main', url: 'https://github.com/ramywageh/test-project.git'
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
        stage("Build") {
            steps {
                sh '''
                   apt update
                    apt install -y sudo docker.io
                    usermod -aG docker $USER
                    docker build -t my-app .
                '''
                
               /* withCredentials([usernamePassword(credentialsId:"docker",usernameVariable:"USER",passwordVariable:"PASS")]){
                sh 'docker build . -t ${USER}/todo-app:v1.${BUILD_NUMBER}'
                sh 'docker login -u ${USER} -p ${PASS}'
                sh 'docker push ${USER}/todo-app:v1.${BUILD_NUMBER}'
                }*/
            }
        }
    }
}