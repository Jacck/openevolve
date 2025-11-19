@echo off
REM Convenience script to run sequential game solver evolution on Windows

echo Sequential Game Solver Evolution
echo ==================================
echo.

REM Check if API key is set
if "%OPENAI_API_KEY%"=="" (
    echo Warning: OPENAI_API_KEY environment variable is not set
    echo Please set it before running evolution:
    echo   set OPENAI_API_KEY=your-key-here
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Get the script directory
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
cd /d %SCRIPT_DIR%\..\..\

echo [1/3] Testing initial program...
cd /d %SCRIPT_DIR%
python initial_program.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Initial program works
) else (
    echo   [FAIL] Initial program failed
)

echo.
echo [2/3] Running evaluator test...
python evaluator.py initial_program.py

echo.
echo [3/3] Starting evolution...
cd /d %SCRIPT_DIR%\..\..\

REM Default to 50 iterations, or use first argument
if "%1"=="" (
    set ITERATIONS=50
) else (
    set ITERATIONS=%1
)

python openevolve-run.py ^
  "%SCRIPT_DIR%\initial_program.py" ^
  "%SCRIPT_DIR%\evaluator.py" ^
  --config "%SCRIPT_DIR%\config.yaml" ^
  --iterations %ITERATIONS%

echo.
echo Evolution complete!
echo Check results in: %SCRIPT_DIR%\openevolve_output\
echo.
echo To visualize results:
echo   python scripts\visualizer.py --path %SCRIPT_DIR%\openevolve_output\checkpoints\checkpoint_%ITERATIONS%\
