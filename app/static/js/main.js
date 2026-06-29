const INITIAL_LIMIT = 50;


const fetchApi = async (url) => {
  const response = await fetch(url);
  return await response.json();
}


document.addEventListener("alpine:init", () => {
  Alpine.data("articleManager", () => ({
    articles: [],
    selectedArticle: {},
    categories: [],
    taxes: [],
    total: 0,
    search: "",
    limit: INITIAL_LIMIT,

    async init() {
      const [articlesData, categoriesData, taxesData] = await Promise.all([
        fetchApi("/api/articles?store=pessac&size=3000"),
        fetchApi("/api/categories"),
        fetchApi("/api/taxes")
      ]);
      this.articles = articlesData.items;
      this.total = articlesData.total;
      this.categories = categoriesData.items;
      this.taxes = taxesData.items;
      console.log(this.taxes);
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

    openEditModal(article) {
      // Create a deep copy
      this.selectedArticle = JSON.parse(JSON.stringify(article));
      this.$dispatch('open-modal');
    },

    async synchronizeArticles() {
      await fetch("/api/articles/synchronize", {method: "POST"});
    }
  }));
});
