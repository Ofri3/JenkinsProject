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
        DOCKER_REPO = 'ofriz/jenkinsproject'
        SNYK_API_TOKEN = credentials('SNYK_API_TOKEN')
    }
    stages {
        stage('Checkout') {
            steps {
                // Checkout code
                checkout scm
            }
        }
        stage('Build, tag, and push docker image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        // Extract Git commit hash
                        bat(script: 'git rev-parse --short HEAD > gitCommit.txt')
                        def gitCommit = readFile('gitCommit.txt').trim()

                        // Define semver
                        def semver = "1.0.${BUILD_NUMBER}" // Example semver

                        // Tag with semver, git commit, and latest
                        def semverTag = "${semver}"
                        def gitTag = "${gitCommit}"
                        def latestTag = "latest"

                        // Build, tag, and push images
                        bat """
                            cd polybot
                            docker login -u ${USER} -p ${PASS}
                            docker build -t %DOCKER_REPO%:${semverTag} -t %DOCKER_REPO%:${gitTag} -t %DOCKER_REPO%:${latestTag} .
                            docker push %DOCKER_REPO%:${latestTag}
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
                            snyk container test %DOCKER_REPO%:latest --severity-threshold=high || exit 0
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
        stage('Static code linting and Unittesting') {
            parallel {
                stage('Static code linting') {
                    steps {
                        script {
                            bat """
                            python -m pylint -f parseable --reports=no polybot/*.py > pylint.log
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
    }
    post {
        always {
            // Type the pylint.log results
            bat 'type pylint.log'

            // Processes the test results using the JUnit plugin
            junit 'results.xml'

            // Processes the pylint report using the Warnings Plugin
            recordIssues (
                aggregatingResults: true,
                tools: [pyLint(pattern: 'pylint.log', severityWarning: 'HIGH')]
            )

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