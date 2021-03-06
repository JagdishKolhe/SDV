import graphviz


def _get_graphviz_extension(path):
    if path:
        path_splitted = path.split('.')
        if len(path_splitted) == 1:
            raise ValueError('Path without graphviz extansion.')

        graphviz_extension = path_splitted[-1]

        if graphviz_extension not in graphviz.backend.FORMATS:
            raise ValueError(
                '"{}" not a valid graphviz extension format.'.format(graphviz_extension)
            )

        return '.'.join(path_splitted[:-1]), graphviz_extension

    return None, None


def _add_nodes(metadata, digraph):
    """Add nodes into a `graphviz.Digraph`.

    Each node represent a metadata table.

    Args:
        metadata (Metadata):
            Metadata object to plot.
        digraph (graphviz.Digraph):
            graphviz.Digraph being built
    """
    for table in metadata.get_tables():
        # Append table fields
        fields = []

        for name, value in metadata.get_fields(table).items():
            if value.get('subtype') is not None:
                fields.append('{} : {} - {}'.format(name, value['type'], value['subtype']))

            else:
                fields.append('{} : {}'.format(name, value['type']))

        fields = r'\l'.join(fields)

        # Append table extra information
        extras = []

        primary_key = metadata.get_primary_key(table)
        if primary_key is not None:
            extras.append('Primary key: {}'.format(primary_key))

        parents = metadata.get_parents(table)
        for parent in parents:
            foreign_key = metadata.get_foreign_key(parent, table)
            extras.append('Foreign key ({}): {}'.format(parent, foreign_key))

        path = metadata.get_table_meta(table).get('path')
        if path is not None:
            extras.append('Data path: {}'.format(path))

        extras = r'\l'.join(extras)

        # Add table node
        title = r'{%s|%s\l|%s\l}' % (table, fields, extras)
        digraph.node(table, label=title)


def _add_edges(metadata, digraph):
    """Add edges into a `graphviz.Digraph`.

    Each edge represents a relationship between two metadata tables.

    Args:
        digraph (graphviz.Digraph)
    """
    for table in metadata.get_tables():
        for parent in list(metadata.get_parents(table)):
            digraph.edge(
                parent,
                table,
                label='   {}.{} -> {}.{}'.format(
                    table, metadata.get_foreign_key(parent, table),
                    parent, metadata.get_primary_key(parent)
                ),
                arrowhead='oinv'
            )


def visualize(metadata, path=None):
    """Plot metadata usign graphviz.

    Try to generate a plot using graphviz.
    If a ``path`` is provided save the output into a file.

    Args:
        metadata (Metadata):
            Metadata object to plot.
        path (str):
            Output file path to save the plot, it requires a graphviz
            supported extension. If ``None`` do not save the plot.
            Defaults to ``None``.
    """
    filename, graphviz_extension = _get_graphviz_extension(path)
    digraph = graphviz.Digraph(
        'Metadata',
        format=graphviz_extension,
        node_attr={
            "shape": "Mrecord",
            "fillcolor": "lightgoldenrod1",
            "style": "filled"
        },
    )

    _add_nodes(metadata, digraph)
    _add_edges(metadata, digraph)

    if filename:
        digraph.render(filename=filename, cleanup=True, format=graphviz_extension)
    else:
        return digraph
