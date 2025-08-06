@echo off
echo ============================================================
echo    FIXING JAVA VERSION ISSUES FOR ANDROID PROJECTS
echo ============================================================

echo.
echo Checking Java installations...
echo.

REM Check if Java 17 is available
if exist "C:\Program Files\Java\jdk-17" (
    echo Found Java 17 at: C:\Program Files\Java\jdk-17
    set JAVA_HOME=C:\Program Files\Java\jdk-17
    set PATH=%JAVA_HOME%\bin;%PATH%
    echo Set JAVA_HOME to Java 17
) else if exist "C:\Program Files\Eclipse Adoptium\jdk-17" (
    echo Found Java 17 at: C:\Program Files\Eclipse Adoptium\jdk-17
    set JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17
    set PATH=%JAVA_HOME%\bin;%PATH%
    echo Set JAVA_HOME to Java 17
) else (
    echo WARNING: Java 17 not found in standard locations
    echo Please install Java 17 (JDK) from: https://adoptium.net/
    pause
    exit /b 1
)

echo.
echo Current Java version:
java -version

echo.
echo ============================================================
echo    FIXING PARADIGM INVENTORY SCANNER
echo ============================================================

cd ParadigmInventoryScanner
echo Cleaning project...
call gradlew clean
echo Building project...
call gradlew assembleDebug
cd ..

echo.
echo ============================================================
echo    FIXING INVENTORY SCANNER APP
echo ============================================================

cd InventoryScannerApp
echo Cleaning project...
call gradlew clean
echo Building project...
call gradlew assembleDebug
cd ..

echo.
echo ============================================================
echo    FIXING SIMPLE PARADIGM SCANNER
echo ============================================================

cd SimpleParadigmScanner
echo Cleaning project...
call gradlew clean
echo Building project...
call gradlew assembleDebug
cd ..

echo.
echo ============================================================
echo    ALL ANDROID PROJECTS FIXED!
echo ============================================================
echo.
echo If you still see Java version errors:
echo 1. Install Java 17 JDK from: https://adoptium.net/
echo 2. Set JAVA_HOME environment variable
echo 3. Restart your IDE
echo.
pause
