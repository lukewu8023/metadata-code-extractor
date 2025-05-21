#!/bin/bash
# Technology Validation Script for Metadata Code Extractor
# Run this script to validate the selected technologies

# Set up colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=========================================================${NC}"
echo -e "${CYAN}     METADATA CODE EXTRACTOR - TECHNOLOGY VALIDATION     ${NC}"
echo -e "${CYAN}=========================================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    # Check if .env.example exists and copy it
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file from .env.example${NC}"
        echo -e "${YELLOW}Please update values in .env file before continuing${NC}"
        echo "Press enter to continue or Ctrl+C to abort..."
        read
    else
        echo -e "${RED}Error: .env.example not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n${CYAN}Creating virtual environment...${NC}"
    python -m venv .venv
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "\n${CYAN}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"

# Check Python version
echo -e "\n${CYAN}Checking Python version...${NC}"
python --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Python not found or cannot be executed${NC}"
    exit 1
fi

# Install required packages
echo -e "\n${CYAN}Installing required packages...${NC}"
pip install python-dotenv pydantic requests openai neo4j chromadb
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install required packages${NC}"
    exit 1
fi
echo -e "${GREEN}Packages installed successfully${NC}"

# Create validation results file with date
RESULTS_FILE="validation_results_$(date +%Y%m%d_%H%M%S).txt"
echo "METADATA CODE EXTRACTOR - TECHNOLOGY VALIDATION RESULTS" > $RESULTS_FILE
echo "Date: $(date)" >> $RESULTS_FILE
echo "=========================================================" >> $RESULTS_FILE

# Function to run a validation test
run_test() {
    local script_name=$1
    local test_name=$2
    
    echo -e "\n${CYAN}=========================================================${NC}"
    echo -e "${CYAN}Running $test_name Validation...${NC}"
    echo -e "${CYAN}=========================================================${NC}"
    
    echo -e "\n$test_name Validation" >> $RESULTS_FILE
    echo "==========================================================" >> $RESULTS_FILE
    
    python $script_name 2>&1 | tee -a $RESULTS_FILE
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "\n${GREEN}$test_name Validation: PASSED${NC}"
        echo -e "\nVALIDATION RESULT: PASSED\n" >> $RESULTS_FILE
    else
        echo -e "\n${RED}$test_name Validation: FAILED${NC}"
        echo -e "\nVALIDATION RESULT: FAILED\n" >> $RESULTS_FILE
    fi
}

# Run all validation tests
run_test "tech_validation/config_poc.py" "Configuration"
run_test "tech_validation/llm_poc.py" "LLM Provider"
run_test "tech_validation/graph_db_poc.py" "Graph Database"
run_test "tech_validation/vector_db_poc.py" "Vector Database"

# Summarize results
echo -e "\n${CYAN}=========================================================${NC}"
echo -e "${CYAN}            VALIDATION SUMMARY                           ${NC}"
echo -e "${CYAN}=========================================================${NC}"

echo -e "\nResults saved to: ${GREEN}$RESULTS_FILE${NC}"
echo -e "Please review this file for detailed validation results."

# Check for PASSED/FAILED status in results file
CONFIG_STATUS=$(grep -A 1 "Configuration Validation" $RESULTS_FILE | grep "VALIDATION RESULT:" | cut -d ":" -f 2)
LLM_STATUS=$(grep -A 1 "LLM Provider Validation" $RESULTS_FILE | grep "VALIDATION RESULT:" | cut -d ":" -f 2)
GRAPH_STATUS=$(grep -A 1 "Graph Database Validation" $RESULTS_FILE | grep "VALIDATION RESULT:" | cut -d ":" -f 2)
VECTOR_STATUS=$(grep -A 1 "Vector Database Validation" $RESULTS_FILE | grep "VALIDATION RESULT:" | cut -d ":" -f 2)

echo -e "\nConfiguration:  ${CONFIG_STATUS}"
echo -e "LLM Provider:   ${LLM_STATUS}"
echo -e "Graph Database: ${GRAPH_STATUS}"
echo -e "Vector Database:${VECTOR_STATUS}"

# Check if any tests failed
if grep -q "VALIDATION RESULT: FAILED" $RESULTS_FILE; then
    echo -e "\n${RED}Some validation tests failed. Please review the results.${NC}"
    echo -e "Fix any issues before proceeding with Phase 1 implementation."
else
    echo -e "\n${GREEN}All validation tests passed!${NC}"
    echo -e "You can now proceed with Phase 1 implementation."
fi

echo -e "\n${CYAN}=========================================================${NC}"
echo -e "${CYAN}            VALIDATION COMPLETE                          ${NC}"
echo -e "${CYAN}=========================================================${NC}"

# Deactivate virtual environment
deactivate
echo -e "\n${GREEN}Virtual environment deactivated${NC}" 