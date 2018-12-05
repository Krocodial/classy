// ================================================================================================
// SonarQube Scanner Settings
// ------------------------------------------------------------------------------------------------

// The name of the SonarQube route.  Used to dynamically get the URL for SonarQube.
def SONAR_ROUTE_NAME = 'sonarqube'

// The name of your SonarQube project
def SONAR_PROJECT_NAME = 'TheOrgBook-Zap'

// The project key of your SonarQube project
def SONAR_PROJECT_KEY = 'TheOrgBook-Zap'

// The base directory of your project.
// This is relative to the location of the `sonar-runner` directory within your project.
// More accurately this is relative to the Gradle build script(s) that manage the SonarQube Scanning
def SONAR_PROJECT_BASE_DIR = '../'

// The source code directory you want to scan.
// This is relative to the project base directory.
def SONAR_SOURCES = './zap/wrk'
// ================================================================================================

// ================================================================================================
// ZAP Scanner Settings
// ------------------------------------------------------------------------------------------------

// The name of the target route.  This will be used to dynamically get the URL.
def TARGET_ROUTE = 'classy'

// The namespace in which the target route can be found.  This will be used to dynamically get the URL.
def TARGET_PROJECT_NAMESPACE = 'l9fjgg-dev'

// The path to the API.
def API_PATH='/api'

// The API format; either openapi or soap
def API_FORMAT = 'openapi'

// The name  of the ZAP report
def ZAP_REPORT_NAME = "zap-report.xml"

// The location of the ZAP reports
def ZAP_REPORT_PATH = "/zap/wrk/${ZAP_REPORT_NAME}"

// The name of the "stash" containing the ZAP report
def ZAP_REPORT_STASH = "zap-report"
// ================================================================================================

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


node {
	
    stage('checkout for static code analysis') {
        echo "checking out source"
        echo "Build: ${BUILD_ID}"
        checkout scm
    }

    stage('code quality check') {
	
        SONAR_LOGIN = sh (
            script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONAR_LOGIN/{print $2}\'',
            returnStdout: true
        ).trim()
        echo "SONAR_LOGIN: ${SONAR_LOGIN}"

		
        SONAR_HOST = sh (
            script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONAR_HOST/{print $2}\'',
            returnStdout: true
        ).trim()
        echo "SONAR_HOST: ${SONAR_HOST}"

		
        sh returnStdout: true, 
		script: "chmod +x sonar-runner/gradlew && ./sonar-runner/gradlew -Dsonar.projectKey=classy -Dsonar.sources=. \
			-Dsonar.host.url=${SONAR_HOST} \
			-Dsonar.login=${SONAR_LOGIN}"
        
    }

	
}
