class QueryBuilder:
    def __init__(self, session) -> None:
        self.session = session
        self.models = []
        self.joins = []
        self.filters = []
        self.orders = []
        self.groups = []
        self.distinct = None

    def add_model(self, model) -> None:
        self.models.append(model)

    def add_join(self, join) -> None:
        self.joins.append(join)

    def add_filter(self, filter) -> None:
        self.filters.append(filter)

    def group_by(self, group) -> None:
        self.groups.append(group)

    def order_by(self, order, desc=False) -> None:
        if desc:
            self.orders.append(order.desc)
        else:
            self.orders.append(order.asc)

    def build(self):
        query = self.session.query(*self.models)

        if self.distinct:
            query = query.distinct(self.distinct)

        for join in self.joins:
            query = query.join(join)
        for filter in self.filters:
            query = query.filter(filter)

        if self.groups:
            for group in self.groups:
                query = query.group_by(group)

        if self.orders:
            for order in self.orders:
                query = query.order_by(order())


        return query
