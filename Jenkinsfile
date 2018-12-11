// Gets the URL associated to a named route.
// If you are attempting to access a route outside the local namespace (the namespace in which this script is running)
// The Jenkins service account from the local namespace will need 'view' access to the remote namespace.
// For example:
// Using the oc cli directly:
//   oc policy add-role-to-user view system:serviceaccount:devex-von-bc-registries-agent-tools:jenkins -n view devex-von-tools
// Or using the openshift-developer-tools (https://github.com/BCDevOps/openshift-developer-tools) sripts:
//   assignRole.sh -u system:serviceaccount:devex-von-bc-registries-agent-tools:jenkins -r view devex-von-tools

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

@NonCPS
String getSonarQubePwd() {

  sonarQubePwd = sh (
    script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONARQUBE_ADMINPW/{print $2}\'',
    returnStdout: true
  ).trim()

  return sonarQubePwd
}

// ================================================================================================
// SonarQube Scanner Settings
// ------------------------------------------------------------------------------------------------
def SONAR_ROUTE_NAME = 'sonarqube'
def SONAR_ROUTE_NAMESPACE = 'l9fjgg-tools'
def SONAR_PROJECT_NAME = 'Data Security classification Repository'
def SONAR_PROJECT_KEY = 'classy'
def SONAR_PROJECT_BASE_DIR = '../'
def SONAR_SOURCES = './'
// ================================================================================================


// The jenkins-python3nodejs template has been purpose built for supporting SonarQube scanning.
pipeline {
  environment {
	SONAR_ROUTE_NAME = 'sonarqube'
	SONAR_ROUTE_NAMESPACE = 'l9fjgg-tools'
	SONAR_PROJECT_NAME = 'Data Security classification Repository'
	SONAR_PROJECT_KEY = 'classy'
	SONAR_PROJECT_BASE_DIR = '../'
	SONAR_SOURCES = './'
  
	SONARQUBE_URL = sh (
		script: "oc get routes sonarqube -o wide --no-headers | awk \'/sonarqube/ {print \"https://\"\$2}\'",
		returnStdout: true
		)
	
    //SONARQUBE_PWD = getSonarQubePwd().trim()
  
  }
  agent any
  stages {
    stage('Checkout Source') {
	  steps {
      echo "Checking out source code ..."
      checkout scm
	  }
    }

    stage('SonarQube Analysis') {
	  steps {
	    script {
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
			      stage('Checkout Source') {
					  echo "Checking out source code ..."
					  checkout scm
				  }
				  stage('SonarQube Analysis') {
					  echo "Performing static SonarQube code analysis ..."

					  echo "URL: ${SONARQUBE_URL}"
					  //echo "PWD: ${SONARQUBE_PWD}"

					  //dir('sonar-runner') {
						// ======================================================================================================
						// Set your SonarQube scanner properties at this level, not at the Gradle Build level.
						// The only thing that should be defined at the Gradle Build level is a minimal set of generic defaults.
						//
						// For more information on available properties visit:
						// - https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+Gradle
						// ======================================================================================================
						TESTO = sh (
						  returnStdout: true,
						  script: "ls"
						).trim()
						
						echo "${TESTO}"
						
						sh (
						  returnStdout: true,
						  script: "chmod +x gradlew"
						)
						
						sh (
						  returnStdout: true,
						  script: "./gradlew sonarqube --stacktrace --info \
							-Dsonar.verbose=true \
							-Dsonar.host.url=${SONARQUBE_URL} \
							-Dsonar.projectName='${SONAR_PROJECT_NAME}' \
							-Dsonar.projectKey=${SONAR_PROJECT_KEY} \
							-Dsonar.projectBaseDir=${SONAR_PROJECT_BASE_DIR} \
							-Dsonar.sources=${SONAR_SOURCES}"
						)
						//}
				  }//stage end
			}//node end
		  }//podTemplate end
		}//script end
	  }//steps end
	}//stage end
  }//end of stages
}//pipeline end