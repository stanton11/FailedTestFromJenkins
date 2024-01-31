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
                    splitRes = env.paramsResult.split('\n')
                    env.params = splitRes[0]
                    env.val = splitRes[1]
                    env.san = splitRes[2]
                    env.p0 = splitRes[3]
                    env.p1 = splitRes[4]
                    env.custom = splitRes[5]
                }
            }
        }

        stage('Run getFailedTest.py') {
            steps {
                script {
                    def customTestsResult = sh(script: 'python3 getFailedTestLW.py ${params.jobName}/${params.buildNumber} ${env.val} ${env.san} ${env.p0} ${env.p1} ${env.custom}', returnStdout: true).trim()
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
