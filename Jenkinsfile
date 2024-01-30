pipeline {
    parameters {
        string(name: 'jobName', description: 'Job Name', defaultValue: 'k8s-cbop-aks-pipeline')
        string(name: 'buildNumber', description: 'Build Number', defaultValue: '685')
    }

    agent any

    stages {
        stage('Download Scripts') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://github.com/stanton11/FailedTestFromJenkins']]])
                }
            }
        }

        stage('Run getParams.py') {
            steps {
                script {
                    env.JOB_NAME = params.jobName
                    env.BUILD_NUMBER = params.buildNumber

                    env.paramsResult = sh(
                        script: 'python3 getParams.py "$JOB_NAME" "$BUILD_NUMBER"',
                        returnStdout: true
                    )
                    print(env.paramsResult)
                }
            }
        }

        stage('Run getFailedTests.py') {
            steps {
                script {
                    def customTestsResult = sh(script: "python3 getFailedTests.py ${params.jobName}/${params.buildNumber} ${params.validation} ${params.sanity} ${params.p0} v${params.p1}", returnStdout: true).trim()
                    env.CUSTOM_TESTS = customTestsResult
                    sh "echo ${env.CUSTOM_TESTS}"
                }
            }
        }

        stage('Build Job') {
            steps {
                script {
                    build job: params.jobName, parameters: env.PARAMS, propagate: false, wait: false, quietPeriod: 3
                }
            }
        }
    }
}
