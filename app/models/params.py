from app.models.model import TopTag


def get_tags():
    tags = TopTag.query.all()

    data = []
    for first in tags:
        second_tags = []
        for second in first.second_tag:
            second_tags.append({
                'id': second.id,
                'tag': second.name
            })
        data.append({
            'top': first.name,
            'second': second_tags
        })

    return data
