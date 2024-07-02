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
                snykSecurity(
                    severity: 'high',
                    snykInstallation: 'snyk@latest',
                    snykTokenId: 'SNYK_API_TOKEN',
                    targetFile: 'polybot/Dockerfile'
                )
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
            // Clean up unused dangling images
            script {
                bat """
                    docker image prune -f
                """
            }
        }
    }
}