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
                    env.customTestsResult = sh(
                        script: 'python3 getFailedTestLW.py "$JOB_NAME"/"$BUILD_NUMBER" "$val" "$san" "$p0" "$p1" "$custom"',
                        returnStdout: true
                    ).trim()
                    echo "Custom Tests Result: ${env.customTestsResult}"
                }
            }
        }

        stage('Build Job') {
            steps {
                script {
                    env.params += env.customTestsResult
                    env.params_list = env.params.split(',')
                    build job: params.jobName, parameters: env.params_list, propagate: false, wait: false, quietPeriod: 3
                }
            }
        }
    }
}
