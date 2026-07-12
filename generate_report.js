const fs = require('fs');
const path = require('path');
const reporter = require('cucumber-html-reporter');

const jsonPath = path.join(__dirname, 'evidence', 'report.json');
const outputPath = path.join(__dirname, 'evidence', 'cucumber_report.html');

console.log("Reading Behave JSON report...");
let data;
try {
  data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
} catch (e) {
  console.error("Error reading JSON file:", e);
  process.exit(1);
}

// Convert Behave format to Cucumber-compliant format
data.forEach(feature => {
  if (!feature.uri && feature.location) {
    feature.uri = feature.location.split(':')[0];
  }
  
  // Convert description array to string
  if (feature.description && Array.isArray(feature.description)) {
    feature.description = feature.description.join('\n');
  }

  if (feature.elements) {
    feature.elements.forEach(scenario => {
      if (!scenario.id) {
        scenario.id = scenario.name.toLowerCase().replace(/[^a-z0-9]/g, '-');
      }
      
      // Convert scenario description array to string
      if (scenario.description && Array.isArray(scenario.description)) {
        scenario.description = scenario.description.join('\n');
      }

      if (scenario.steps) {
        scenario.steps.forEach(step => {
          // Fix missing results or step statuses
          if (!step.result) {
            step.result = { status: 'skipped' };
          }
          // Behave uses seconds, Cucumber HTML Reporter expects nanoseconds
          if (step.result.duration) {
            step.result.duration = Math.round(step.result.duration * 1000000000);
          }
        });
      }
    });
  }
});

// Save the converted JSON back to the file
fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2));
console.log("JSON report converted to Cucumber format.");

// Reporter options
const options = {
  theme: 'bootstrap',
  jsonFile: jsonPath,
  output: outputPath,
  reportSuiteAsScenarios: true,
  scenarioTimestamp: true,
  launchReport: false,
  metadata: {
    "Test Environment": "QA Practice E-Commerce & REST API",
    "Browser": "Chrome (Headless)",
    "Platform": "Windows/Docker",
    "Framework": "Behave (Python) & Selenium",
    "Generated At": new Date().toLocaleString()
  }
};

console.log("Generating HTML report...");
try {
  reporter.generate(options);
  console.log(`HTML report generated successfully at: ${outputPath}`);
} catch (e) {
  console.error("Error generating report:", e);
  process.exit(1);
}
