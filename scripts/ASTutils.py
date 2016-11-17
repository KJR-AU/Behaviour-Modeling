# utility methods for managing the Gherkin AST

updateLineNumbers(feature,offset,increment)
{
    for key,value in feature['feature']:
        if (key == 'children'):
            for child in value:
                for step in child['steps']
                    if step['location']['line'] > offset:
                        step['location']['line'] = step['location']['line'] + increment
    for comment in feature['comments']
        if comment['location']['line'] > offset:
            comment['location']['line'] = comment['location']['line'] + increment
}

