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

                    env.splitRes = env.paramsResult.split('\n')
                    env.new_params = env.splitRes[0]
                    env.val = env.splitRes[1]
                    env.san = env.splitRes[2]
                    env.p0 = env.splitRes[3]
                    env.p1 = env.splitRes[4]
                    env.custom = env.splitRes[5]

                    print('vars: ' + env.new_params + ' ' + env.val + ' ' + env.san + ' ' + env.p0 + ' ' + env.p1 + ' ' + env.custom)
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
                    env.splitOut = env.customTestsResult.split('\n')
                    env.customTestsResult = env.splitOut.last()
                    echo "Custom Tests Result: ${env.customTestsResult}"
                }
            }
        }

        stage('Build Job') {
            steps {
                script {
                    // Build Param Set
                    env.new_params += env.customTestsResult
                    env.param_list = env.new_params.tokenize(',')

                    // Initialize an empty list to store parameters
                    env.paramsObjects = []

                    // Define the processElement function
                    def processElement = { element ->
                        // Extract class, name, and value from the element
                        paramClass = element[0]
                        paramName = element.name
                        paramValue = element.value

                        // Determine the class based on the value
                        paramType = paramValue instanceof Boolean ? 'BooleanParameterValue' : 'StringParameterValue'

                        // Build the parameter object and push it to the list
                        env.paramsObjects.add([$class: paramType, name: paramName, value: paramValue])
                    }

                    // Loop through each element in the input list
                    env.param_list.each {
                        processElement(it)
                    }

                    print(env.paramsObjects)

                    build job: env.JOB_NAME, parameters: env.paramsObjects, propagate: false, wait: false, quietPeriod: 3
                }
            }
        }
    }
}
