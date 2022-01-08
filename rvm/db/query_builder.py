class QueryBuilder:
    def __init__(self, session) -> None:
        self.session = session
        self.models = []
        self.joins = []
        self.filters = []
        self.order = None
        self.distinct = None

    def add_model(self, model) -> None:
        self.models.append(model)

    def add_join(self, join) -> None:
        self.joins.append(join)

    def add_filter(self, filter) -> None:
        self.filters.append(filter)

    def order_by(self, order, desc=False) -> None:
        if desc:
            self.order = order.desc
        else:
            self.order = order.asc

    def build(self):
        query = self.session.query(*self.models)

        if self.distinct:
            query = query.distinct(self.distinct)

        for join in self.joins:
            query = query.join(join)
        for filter in self.filters:
            query = query.filter(filter)

        if self.order:
            query = query.order_by(self.order())


        return query
