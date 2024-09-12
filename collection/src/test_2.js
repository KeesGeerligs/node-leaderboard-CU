import { extractBenchmarkResults} from "./utils/extractBenchmarkResults.js"

const results = {}
const test_result = {
  // ADD YOUR RESULT JSON HERE
}

extractBenchmarkResults(results, test_result);

console.log(results)