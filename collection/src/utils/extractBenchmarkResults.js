export function extractBenchmarkResults(results, jobResult) {
  [
    "gemma_results",
    "phi3_results",
    "mistral_results",
    "llama3_results",
    "qwen_results",
    "llama3_70b_results"
  ].forEach((name) => {
    const modelResults = results[name];
    if (modelResults && modelResults.length > 0) {
      let totalTokens = 0;
      let totalDecodingSeconds = 0;
      let totalInferenceSeconds = 0;

      modelResults.forEach((resultStr) => {
        try {
          const cleanedString = resultStr.replace(/'/g, '"');
          const modelData = JSON.parse(cleanedString);

          totalTokens += parseInt(modelData.total_tokens, 10);
          totalDecodingSeconds += parseFloat(modelData.total_decoding_seconds);
          totalInferenceSeconds += parseFloat(
            modelData.total_inference_seconds
          );
        } catch (error) {
          console.error(`Error parsing ${name} JSON:`, error.message);
        }
      });

      jobResult.data.performance[name.replace("_results", "")] = {
        totalInferenceSeconds: parseFloat(totalInferenceSeconds.toFixed(2)),
        producedTokens: parseInt(totalTokens),
        decodingSeconds: parseFloat(totalDecodingSeconds.toFixed(2)),
        tokensPerSecond: parseFloat(
          (totalTokens / totalDecodingSeconds).toFixed(2)
        ),
      };
    }
  });
}
