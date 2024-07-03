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
                            docker push %DOCKER_REPO%:${semverTag}
                            docker push %DOCKER_REPO%:${gitTag}
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
                    bat 'pip install pytest unittest2'
                }
            }
        }

        stage('Unittest') {
            steps {
                script {
                    bat 'python -m pytest --junitxml results.xml polybot/test/*.py'
                }
            }
        }
    }
    post {
            // Clean up workspace after build
        always {
            cleanWs(cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    disableDeferredWipeout: true,
                    notFailBuild: true)

            // Publishes the test results in a readable format within Jenkins.
            junit allowEmptyResults: true, testResults: 'results.xml'

            // Clean up unused dangling images
            script {
                bat """
                    docker image prune -f
                """
            }
        }
    }
}