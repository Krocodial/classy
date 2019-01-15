
@NonCPS
String getUrlForRoute(String routeName, String projectNameSpace = '') {

  def nameSpaceFlag = ''
  if(projectNameSpace?.trim()) {
    nameSpaceFlag = "-n ${projectNameSpace}"
  }
  
  def url = sh (
    script: "oc get routes ${nameSpaceFlag} -o wide --no-headers | awk \'/${routeName}/{ print match(\$0,/edge/) ?  \"https://\"\$2 : \"http://\"\$2 }\'",
    returnStdout: true
  ).trim()

  return url
}

def deployTemplates(String name, String env, String pr, String git_repo, String git_branch, String databaseBC, String backendDC, String databaseDC, String nginxDC) {

	databasePVC = openshift.process(
		readFile(file:"${databaseBC}"))
		
	openshift.apply(databasePVC)
	
	database = openshift.process(
		readFile(file:"${databaseDC}"),
		"-p", 
		"APP_NAME=${name}", 
		"NAME_SUFFIX=${env}-${pr}", 
		"ENV_NAME=${env}", 
		"APP_IMAGE_TAG=${pr}", 
		"SOURCE_REPOSITORY_URL=${git_repo}", 
		"SOURCE_REPOSITORY_REF=${git_branch}")
	
	
	backend = openshift.process(
		readFile(file:"${backendDC}"),
		"-p", 
		"APP_NAME=${name}", 
		"NAME_SUFFIX=${env}-${pr}", 
		"ENV_NAME=${env}", 
		"APP_IMAGE_TAG=${pr}", 
		"SOURCE_REPOSITORY_URL=${git_repo}", 
		"SOURCE_REPOSITORY_REF=${git_branch}")
	
	nginx = openshift.process(
		readFile(file:"${nginxDC}"),
		"-p",
		"APP_NAME=${name}", 
		"NAME_SUFFIX=${env}-${pr}", 
		"ENV_NAME=${env}", 
		"APP_IMAGE_TAG=${pr}", 
		"APPLICATION_DOMAIN=${name}-${env}.pathfinder.gov.bc.ca")
	
	
	openshift.apply(database)
		.label(['app':"classy-${env}", 
		'app-name':"${name}", 
		'env-name':"${env}"], 
		"--overwrite")
	
	openshift.apply(backend)
		.label(['app':"classy-${env}", 
		'app-name':"${name}", 
		'env-name':"${env}"], 
		"--overwrite")

	openshift.apply(nginx)
		.label(['app':"classy-${env}", 
		'app-name':"${name}", 
		'env-name':"${env}"], 
		"--overwrite")
}


def backendBC = 'openshift/templates/classy-bc.json'
def databaseBC = 'openshift/templates/postgres-bc.json'
def nginxBC = 'openshift/templates/nginx-bc.json'

def backendDC = 'openshift/templates/classy-dc.json'
def databaseDC = 'openshift/templates/postgres-dc.json'
def nginxDC = 'openshift/templates/nginx-dc.json'

def backendBcTag = 'classy-bc'
def backendDcTag = 'classy-dc'
def databaseDcTag = 'postgres-dc'
def databaseBcTag = 'postgres-bc'
def nginxBcTag = 'nginx-bc'
def nginxDcTag = 'nginx-dc'

def appName = 'classy'

pipeline {
  environment {
  
	APP_NAME = 'classy'
	
	GIT_REPOSITORY = 'https://github.com/Krocodial/classy.git'
	GIT_REF = 'master'
	
	PR_NUM = "${BUILD_NUMBER}"
	
	TOOLS_PROJECT = 'l9fjgg-tools'
	
	DEV_PROJECT = 'l9fjgg-dev'
	DEV_SUFFIX = 'dev'
	DEV_HOST = 'classy-dev.pathfinder.gov.bc.ca'
  
	TEST_PROJECT = 'l9fjgg-test'
	TEST_SUFFIX = 'test'
	TEST_HOST = 'classy-test.pathfinder.gov.bc.ca'
  
	PROD_PROJECT = 'l9fjgg-prod'
	PROD_SUFFIX = 'prod'
	PROD_HOST = 'classy-prod.pathfinder.gov.bc.ca'
  
	SONAR_ROUTE_NAME = 'sonarqube'
	SONAR_ROUTE_NAMESPACE = 'l9fjgg-tools'
	SONAR_PROJECT_NAME = 'Data Security classification Repository'
	SONAR_PROJECT_KEY = 'classy'
	SONAR_PROJECT_BASE_DIR = '../classy/'
	SONAR_SOURCES = './'
  
	SONARQUBE_URL = sh (
		script: "oc get routes sonarqube -o wide --no-headers | awk \'/sonarqube/ {print \"https://\"\$2}\'",
		returnStdout: true
		)
	
	TARGET_ROUTE = 'proxy-nginx'
	TARGET_PROJECT_NAMESPACE = 'l9fjgg-dev'
	ZAP_REPORT_NAME = "zap-report.xml"
	ZAP_REPORT_PATH = "/zap/wrk/${ZAP_REPORT_NAME}"
	ZAP_REPORT_STASH = "zap-report"
  }
  
  agent any
  options {
	timeout(time: 20, unit: 'MINUTES')
  }
  stages {
	stage('preamble & sweeping floor') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						echo "Destroying backend objects..."
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : nginxBcTag ]).delete()
					}
				}
			}
		}
	}// end of stage
	stage('Preparing build configs && building images') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						backend = openshift.process(
							readFile(file:"${backendBC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}")

						openshift.apply(backend)
						
						nginx = openshift.process(
							readFile(file:"${nginxBC}"),
							"-p",
							"APP_NAME=${APP_NAME}",
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}",
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}"
							)
							
						openshift.apply(nginx)
						
						echo "select 'bc' ${APP_NAME}-${DEV_SUFFIX}-${PR_NUM} and run startBuild() on them"
						def builds = openshift.selector("bc",
							"${APP_NAME}")
						builds.startBuild("--wait", "--env=ENABLE_DATA_ENTRY=True")

						echo "building nginx bc"
						def nginx = openshift.selector("bc", 
							"proxy-nginx-${PR_NUM}")
						nginx.startBuild("--wait")
						
					}
				}
			}
		}
	}// end of stage
	stage('SonarQ scan') {
	  steps {
        script {
			openshift.withCluster() {
				openshift.withProject(TOOLS_PROJECT) {
					checkout scm
					echo "Performing static SonarQube code analysis ..."

					
					echo "URL: ${SONARQUBE_URL}"
					//echo "PWD: ${SONARQUBE_PWD}"

					dir('sonar-runner') {
						sh (
						  returnStdout: true,
						  script: "chmod +x gradlew"
						)
						
						
						SONAR_OUT = sh (
						  returnStdout: true,
						  script: "./gradlew sonarqube --stacktrace --info \
							-Dsonar.verbose=true \
							-Dsonar.projectName='${SONAR_PROJECT_NAME}' \
							-Dsonar.projectKey=${SONAR_PROJECT_KEY} \
							-Dsonar.projectBaseDir=${SONAR_PROJECT_BASE_DIR} \
							-Dsonar.sources=${SONAR_SOURCES} \
							-Dsonar.host.url=${SONARQUBE_URL}"

						)
						echo "${SONAR_OUT}"
					}//sonar-runner end
					}
				}//script end
			}
		}
	  //steps end
	}// end of stage
	/*stage('cleaning dev space') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						echo "Destroying backend objects..."
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : backendDcTag ]).delete()
						openshift.selector("all", [ template : databaseDcTag ]).delete()
						openshift.selector("all", [ template : nginxDcTag ]).delete()
						if (openshift.selector("secrets", "classy-dev").exists()) {
							openshift.selector("secrets", "classy-dev").delete()
						}
					}
				}
			}
		}
	}*/ // end of stage
	stage('deploy to dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						input "Ready to promote to DEV?"
						
						deployTemplates(
							APP_NAME, 
							DEV_SUFFIX, 
							PR_NUM, 
							GIT_REPOSITORY, 
							GIT_REF, 
							databaseBC, 
							backendDC, 
							databaseDC, 
							nginxDC)
						
					}
				}
			}
		}
	}// end of stage
	stage('Promoting images to dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
					
						openshift.tag("${TOOLS_PROJECT}/classy:${PR_NUM}",
							"${DEV_PROJECT}/classy:dev")
							
						openshift.tag("${TOOLS_PROJECT}/proxy-nginx:${PR_NUM}",
							"${DEV_PROJECT}/proxy-nginx-${DEV_SUFFIX}:dev")
							
						def dcs = openshift.selector("dc", [ app : 'classy-dev' ])
						dcs.rollout().latest()
							
						dcs.rollout().status()
							
					}
				}
			}
		}
	}// end of stage
	stage('ZAP & SonarQube scan') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(TOOLS_PROJECT) {
						podTemplate(
						  label: 'owasp-zap', 
						  name: 'owasp-zap', 
						  serviceAccount: 'jenkins', 
						  cloud: 'openshift', 
						  containers: [
							containerTemplate(
							  name: 'jnlp',
							  image: '172.50.0.2:5000/openshift/jenkins-slave-zap',
							  resourceRequestCpu: '500m',
							  resourceLimitCpu: '1000m',
							  resourceRequestMemory: '3Gi',
							  resourceLimitMemory: '4Gi',
							  workingDir: '/home/jenkins',
							  command: '',
							  args: '${computer.jnlpmac} ${computer.name}'
							)
						  ]
						){
						  node('owasp-zap') {
							stage('ZAP Security Scan') {

							  def TARGET_URL = getUrlForRoute(TARGET_ROUTE, TARGET_PROJECT_NAMESPACE).trim()

							  echo "Target URL: ${TARGET_URL}"
							  //echo "API Target URL: ${API_TARGET_URL}"

							  dir('zap') {

								// The ZAP scripts are installed on the root of the jenkins-slave-zap image.
								// When running ZAP from there the reports will be created in /zap/wrk/ by default.
								// ZAP has problems with creating the reports directly in the Jenkins
								// working directory, so they have to be copied over after the fact.
								def retVal = sh (
								  returnStatus: true,
								  //script: "/zap/zap-baseline.py -x ${ZAP_REPORT_NAME} -t ${TARGET_URL}"
								  // Other scanner options ...
								  // zap-api-scan errors out
								  // script: "/zap/zap-api-scan.py -x ${ZAP_REPORT_NAME} -t ${API_TARGET_URL} -f ${API_FORMAT}"
								   script: "/zap/zap-full-scan.py -x ${ZAP_REPORT_NAME} -t ${TARGET_URL}"
								)
								echo "Return value is: ${retVal}"

								// Copy the ZAP report into the Jenkins working directory so the Jenkins tools can access it.
								sh (
								  returnStdout: true,
								  script: "mkdir -p ./wrk/ && cp ${ZAP_REPORT_PATH} ./wrk/"
								)
							  }

							  // Stash the ZAP report for publishing in a different stage (which will run on a different pod).
							  echo "Stash the report for the publishing stage ..."
							  stash name: "${ZAP_REPORT_STASH}", includes: "zap/wrk/*.xml"
							}
						  }
						}

						// The jenkins-python3nodejs template has been purpose built for supporting SonarQube scanning.
						podTemplate(
						  label: 'jenkins-python3nodejs',
						  name: 'jenkins-python3nodejs',
						  serviceAccount: 'jenkins',
						  cloud: 'openshift',
						  containers: [
							containerTemplate(
							  name: 'jnlp',
							  image: '172.50.0.2:5000/openshift/jenkins-slave-python3nodejs',
							  resourceRequestCpu: '1000m',
							  resourceLimitCpu: '2000m',
							  resourceRequestMemory: '2Gi',
							  resourceLimitMemory: '4Gi',
							  workingDir: '/tmp',
							  command: '',
							  args: '${computer.jnlpmac} ${computer.name}'
							)
						  ]
						){
						  node('jenkins-python3nodejs') {

							stage('Publish ZAP Report to SonarQube') {

							  echo "Checking out the sonar-runner folder ..."
							  checkout([
								  $class: 'GitSCM',
								  branches: scm.branches,
								  extensions: scm.extensions + [
									[$class: 'SparseCheckoutPaths',  sparseCheckoutPaths:[[path:'sonar-runner/']]]
								  ],
								  userRemoteConfigs: scm.userRemoteConfigs
							  ])
							  

							  echo "Preparing the report for the publishing ..."
							  unstash name: "${ZAP_REPORT_STASH}"

							  SONARQUBE_URL = getUrlForRoute(SONAR_ROUTE_NAME).trim()
							  //SONARQUBE_PWD = getSonarQubePwd().trim()
							  echo "URL: ${SONARQUBE_URL}"
							  //echo "PWD: ${SONARQUBE_PWD}"

							  echo "Publishing the report ..."
							  // The `sonar-runner` MUST exist in your project and contain a Gradle environment consisting of:
							  // - Gradle wrapper script(s)
							  // - A simple `build.gradle` file that includes the SonarQube plug-in.
							  //
							  // An example can be found here:
							  // - https://github.com/BCDevOps/sonarqube
							  dir('sonar-runner') {
								// ======================================================================================================
								// Set your SonarQube scanner properties at this level, not at the Gradle Build level.
								// The only thing that should be defined at the Gradle Build level is a minimal set of generic defaults.
								//
								// For more information on available properties visit:
								// - https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+Gradle
								// ======================================================================================================
								sh (
								script: "chmod +x gradlew"
								)
								
								sh (
								  // 'sonar.zaproxy.reportPath' must be set to the absolute path of the xml formatted ZAP report.
								  // Exclude the report from being scanned as an xml file.  We only care about the results of the ZAP scan.
								  returnStdout: true,
								  script: "./gradlew sonarqube --stacktrace --info \
									-Dsonar.verbose=true \
									-Dsonar.host.url=${SONARQUBE_URL} \
									-Dsonar.projectName='${SONAR_PROJECT_NAME}' \
									-Dsonar.projectKey=${SONAR_PROJECT_KEY} \
									-Dsonar.projectBaseDir=../ \
									-Dsonar.sources=${SONAR_SOURCES} \
									-Dsonar.zaproxy.reportPath=${WORKSPACE}${ZAP_REPORT_PATH} \
									-Dsonar.exclusions=**/*.xml"
								)
							  }
							}
						  }
						}
					}
				}
			}
		}//steps end
	}// end of stage
	/*stage('Integrations tests') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
					input "Ready to promote to TEST?"
					}
				}
			}
		}
	}// end of stage
    */
    stage('deploy to test') {
        steps {
            script {
                openshift.withCluster() {
                    openshift.withProject(TEST_PROJECT) {
                        input "Ready to promote to TEST?"

                        deployTemplates(
                            APP_NAME,
                            TEST_SUFFIX,
                            PR_NUM,
                            GIT_REPOSITORY,
                            GIT_REF,
                            databaseBC,
                            backendDC,
                            databaseDC,
                            nginxDC)

                    }
                }
            }
        }
    }// end of stage
    stage('Promoting images to test') {
        steps {
            script {
                openshift.withCluster() {
                    openshift.withProject(TEST_PROJECT) {

                        openshift.tag("${TOOLS_PROJECT}/classy:${PR_NUM}",
                            "${TEST_PROJECT}/classy:test")

                        openshift.tag("${TOOLS_PROJECT}/proxy-nginx:${PR_NUM}",
                            "${TEST_PROJECT}/proxy-nginx-${TEST_SUFFIX}:test")

                        def dcs = openshift.selector("dc", [ app : 'classy-test' ])
                        dcs.rollout().latest()

                        dcs.rollout().status()

                    }
                }
            }
        }
    }// end of stage
    stage('deploy to prod') {
        steps {
            script {
                openshift.withCluster() {
                    openshift.withProject(PROD_PROJECT) {
                        input "Ready to promote to PROD?"

                        deployTemplates(
                            APP_NAME,
                            PROD_SUFFIX,
                            PR_NUM,
                            GIT_REPOSITORY,
                            GIT_REF,
                            databaseBC,
                            backendDC,
                            databaseDC,
                            nginxDC)

                    }
                }
            }
        }
    }// end of stage
    stage('Promoting images to prod') {
        steps {
            script {
                openshift.withCluster() {
                    openshift.withProject(PROD_PROJECT) {

                        openshift.tag("${TOOLS_PROJECT}/classy:${PR_NUM}",
                            "${PROD_PROJECT}/classy:prod")

                        openshift.tag("${TOOLS_PROJECT}/proxy-nginx:${PR_NUM}",
                            "${PROD_PROJECT}/proxy-nginx-${PROD_SUFFIX}:prod")

                        def dcs = openshift.selector("dc", [ app : 'classy-prod' ])
                        dcs.rollout().latest()

                        dcs.rollout().status()

                    }
                }
            }
        }
    }// end of stage

  }//end of stages
}//pipeline end



		  
