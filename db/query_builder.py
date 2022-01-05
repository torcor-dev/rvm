class QueryBuilder:
    def __init__(self, session) -> None:
        self.session = session
        self.models = []
        self.joins = []
        self.filters = []

    def add_model(self, model) -> None:
        self.models.append(model)

    def add_join(self, join) -> None:
        self.joins.append(join)

    def add_filter(self, filter) -> None:
        self.filters.append(filter)

    def build(self):
        query = self.session.query(*self.models)
        for join in self.joins:
            query = query.join(join)
        for filter in self.filters:
            query = query.filter(filter)

        return query
