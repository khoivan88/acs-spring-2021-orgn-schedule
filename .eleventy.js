module.exports = function (eleventyConfig) {
  eleventyConfig.setLiquidOptions({
    dynamicPartials: true,
  });

  // Static assets to pass through
  eleventyConfig.addPassthroughCopy('./src/images');

  // Sort with `Array.sort`
  eleventyConfig.addFilter("date_ascending", function(data) {
    return data.sort(function(a, b) {
      return new Date(a.date) - new Date(b.date); // sort by date - ascending
    });
  });

  // Filter by date
  eleventyConfig.addFilter("date_filter", function(data, date) {
    return data.filter(function(item) {
      return item.date === date; // sort by date - ascending
    });
  });

  return {
    dir: {
      input: 'src',
      // includes: '../_includes',
      // output: '_output',
    },
    // markdownTemplateEngine: 'njk',
    // htmlTemplateEngine: 'njk',
  };
};
