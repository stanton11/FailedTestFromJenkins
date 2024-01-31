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
                    ).trim()
                    splitRes = env.paramsResult.tokenize('\n')
                    env.new_params = splitRes[0]
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
                    env.customTestsResult = env.customTestsResult.split('\n').last()
                    echo "Custom Tests Result: ${env.customTestsResult}"
                }
            }
        }

        stage('Build Job') {
            steps {
                script {
                    // Build Param Set
                    env.new_params += env.customTestsResult

                    print('paramsObject: ' + env.new_params)

                    env.jName = "'" + env.JOB_NAME + "'"

                    param_list = env.new_params.tokenize('|')
                    print('param list 0: ' + param_list[0])
                    paramsObject = []

                    for (param in param_list) {
                        paramsObject.add(param)
                    }

                    build job:env.jName, parameters: paramsObject
                }
            }
        }
    }
}
