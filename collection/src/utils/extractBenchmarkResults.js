export function extractBenchmarkResults(results, jobResult) {
  console.log("Input Results:", JSON.stringify(results, null, 2));

  const resultCategories = [
    "results_CU_100",
    "results_CU_50",
    "results_CU_10",
    "results_CU_5",
    "results_CU_1",
    "gemma_results",
    "phi3_results",
    "mistral_results",
    "llama3_results",
    "qwen_results",
    "llama3_70b_results"
  ];

  resultCategories.forEach((name) => {
    const modelResults = results[name];
    if (modelResults && modelResults.length > 0) {
      if (name.includes("results_CU")) {
        // Process CU results
        let totalTokensProduced = 0;
        let totalDuration = 0;
        let totalRequestsMade = 0;
        let totalLatency = 0;
        let count = 0;
        let concurrentUsers = parseInt(name.split('_')[2], 10); // Extract CU value from the name upfront

        modelResults.forEach((resultStr) => {
          try {
            const cleanedString = resultStr.replace(/'/g, '"').replace(/NaN/g, 'null');
            const modelData = JSON.parse(cleanedString);

            totalTokensProduced += parseInt(modelData.total_tokens_produced, 10);
            totalDuration += parseFloat(modelData.total_duration);
            totalRequestsMade += parseInt(modelData.total_requests_made, 10);
            totalLatency += parseFloat(modelData.average_latency);
            count++;
          } catch (error) {
            console.error(`Error parsing ${name} JSON:`, error.message);
          }
        });

        const avgLatency = count > 0 ? totalLatency / count : 0;

        jobResult.data.performance[name] = {
          totalDuration: parseFloat(totalDuration.toFixed(2)),
          totalTokensProduced: parseInt(totalTokensProduced),
          totalRequestsMade: parseInt(totalRequestsMade),
          averageTokensPerSecond: parseFloat((totalTokensProduced / totalDuration).toFixed(2)),
          averageLatency: parseFloat(avgLatency.toFixed(2)),
          concurrentUsers: concurrentUsers,
        };
      } else {
        // Process non-CU results
        let totalTokens = 0;
        let totalDecodingSeconds = 0;
        let totalInferenceSeconds = 0;

        modelResults.forEach((resultStr) => {
          try {
            const cleanedString = resultStr.replace(/'/g, '"').replace(/NaN/g, 'null');
            const modelData = JSON.parse(cleanedString);

            totalTokens += parseInt(modelData.total_tokens, 10);
            totalDecodingSeconds += parseFloat(modelData.total_decoding_seconds);
            totalInferenceSeconds += parseFloat(modelData.total_inference_seconds);

            console.log(`Processed ${name}:`, JSON.stringify(modelData, null, 2));
          } catch (error) {
            console.error(`Error parsing ${name} JSON:`, error.message);
          }
        });

        jobResult.data.performance[name.replace("_results", "")] = {
          totalInferenceSeconds: parseFloat(totalInferenceSeconds.toFixed(2)),
          producedTokens: parseInt(totalTokens),
          decodingSeconds: parseFloat(totalDecodingSeconds.toFixed(2)),
          tokensPerSecond: parseFloat((totalTokens / totalDecodingSeconds).toFixed(2)),
        };
      }
    }
  });
  console.log("Final JobResult:", JSON.stringify(jobResult, null, 2));
}
