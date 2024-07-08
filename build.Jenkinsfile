pipeline {
    agent any
    options {
        // Keeps builds for the last 30 days.
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        // Prevents concurrent builds of the same pipeline.
        disableConcurrentBuilds()
        // Adds timestamps to the log output.
        timestamps()
    }

    environment {
        APP_IMAGE_NAME = 'app-image'
        WEB_IMAGE_NAME = 'web-image'
        GITCOMMIT = bat(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        IMAGE_TAG = "v1.0.0-${BUILD_NUMBER}-${GITCOMMIT}"
        DOCKER_COMPOSE_FILE = 'compose.yaml'
        DOCKER_REPO = 'ofriz/jenkinsproject'
        NEXUS_REPO = "dockernexus"
        NEXUS_PROTOCOL = "http"
        NEXUS_URL = "172.30.134.43:8085"
        NEXUS_CREDENTIALS_ID = 'NEXUS_CREDENTIALS_ID'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        SNYK_API_TOKEN = 'SNYK_API_TOKEN'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image using docker-compose
                    bat """
                        docker-compose -f ${DOCKER_COMPOSE_FILE} build
                    """
                }
            }
        }
        stage('Build, tag, and push docker image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'NEXUS_CREDENTIALS_ID', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        bat """
                            cd polybot
                            docker login -u ${USER} -p ${PASS} ${NEXUS_PROTOCOL}://${NEXUS_URL}/repository/${NEXUS_REPO}
                            docker tag ${APP_IMAGE_NAME}:latest ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                            docker tag ${WEB_IMAGE_NAME}:latest ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${NEXUS_URL}/${APP_IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${NEXUS_URL}/${WEB_IMAGE_NAME}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }
        stage('Security vulnerability scanning') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'SNYK_API_TOKEN', variable: 'SNYK_TOKEN')]) {
                        // Scan the image
                        bat """
                            snyk auth $SNYK_TOKEN
                            snyk container test {APP_IMAGE_NAME}:latest --severity-threshold=high || exit 0
                        """
                    }
                }
            }
        }
        stage('Install Python Requirements') {
            steps {
                script {
                bat """
                pip install --upgrade pip
                pip install pytest unittest2 pylint flask telebot Pillow loguru matplotlib
                """
                }
            }
        }
        stage('Static code linting and Unittest') {
            parallel {
                stage('Static code linting') {
                    steps {
                        script {
                            bat """
                            python -m pylint -f parseable --reports=no polybot/*.py > pylint.log
                            type pylint.log
                            """
                        }
                    }
                }
                stage('Unittest') {
                    steps {
                        script {
                            bat 'python -m pytest --junitxml results.xml polybot/test'
                        }
                    }
                }
            }
        }
        stage('Deployment to EC2') {
            steps {
                // Add deployment steps here
                bat """
                    echo Example: Push Docker image to a registry
                    echo Example: Deploy to EC2
                """
            }
        }
    }

    post {
        always {
            node {
                // Processes the test results using the JUnit plugin
                junit 'results.xml'

                // Processes the pylint report using the Warnings Plugin
                recordIssues enabledForFailure: true, aggregatingResults: true
                recordIssues tools: [pyLint(pattern: 'pylint.log')]

                // Clean up workspace after build
                cleanWs(cleanWhenNotBuilt: false,
                        deleteDirs: true,
                        notFailBuild: true)

                // Clean up unused dangling images
                script {
                    bat """
                        docker image prune -f
                    """
                }
            }
        }
    }
}