@echo off
echo Fixing Android Build Java Version Compatibility...
echo.

echo Setting JAVA_HOME to Java 17...
set JAVA_HOME=C:\Program Files\Java\jdk-17
set PATH=%JAVA_HOME%\bin;%PATH%

echo Current Java version:
java -version

echo.
echo Building Android app...
cd ParadigmInventoryScanner
.\gradlew clean build

echo.
echo Build complete! Check for any remaining errors.
pause
