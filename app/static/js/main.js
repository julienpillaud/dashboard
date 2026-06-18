const INITIAL_LIMIT = 50;

document.addEventListener("alpine:init", () => {
  Alpine.data("articleManager", () => ({
    articles: [],
    total: 0,
    search: "",
    limit: INITIAL_LIMIT,

    async init() {
      const response = await fetch("/api/articles");
      const result = await response.json();
      this.articles = result.items;
      this.total = result.total;
    },

    resetLimit() {
      this.limit = INITIAL_LIMIT;
    },
    loadMore() {
      this.limit += INITIAL_LIMIT;
    },

    get allFiltered() {
      const query = this.search.toLowerCase();
      if (!query) {
        return this.articles.slice(0, this.limit);
      }

      return this.articles
        .filter(article => {
          const name = article.raw?.name?.toLowerCase() || "";
          const category = article.category?.toLowerCase() || "";
          return name.includes(query) || category.includes(query);
        });
    },

    get filteredArticles() {
      return this.allFiltered.slice(0, this.limit);
    },

    get filteredTotal() {
      return this.allFiltered.length;
    },

    async synchronizeArticles() {
      await fetch("/api/articles/synchronize", {method: "POST"});
    }
  }));
});
