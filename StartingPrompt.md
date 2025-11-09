### Create a Python Project to deploy an Azure Function with three key operations

Make sure venv is used for managing the python environment.

## Operation 1 - findCVOnHomepage

The function is responsible for finding a CV file from a starting website homepage URL.  If a document connot be found then the most appropriate HTML page on the candidate's website should be used.  It should follow links to a depth a 3 links if the CV file is not on the website homepage.  Make sure the document returned is only a CV, use synonyms when looking for a CV.

# It should take the following parameters:

 - apiKey - a uid that provides minimal protection for the function.  It should return 401 - Unauthorised if the key is not present or incorrect
 - url - The homepage URL to search from

# It should return the following status codes and fields

**It should return 401 - Unauthorised if the key is not present or incorrect**
 - statusCode - 401
 - statusCodeDescription - Unauthorized

**A successful (200) call should return the following fields**
 - documentName - the filename of the document
 - documentLink - the URI of the document
 - documentType - the content type of the document
 - documentContent - a base64 encodeed representation of the document
 - statusCode - 200
 - statusCodeDescription - OK

**If a document or HTML representation of the CV is not found a 404 status code and message should be returned.**
 - statusCode - 404
 - statusCodeDescription - Not Found

## Operation 2 - wordToPlainText

This function should take the base64 encoded representation of a word document and return the plain text equivilent.  Make sure the plain text is formatted nicely so it bares resemblence to the original layout and formatting of the word document.

It should use the same apiKey as Operation 1.

**It should return 401 - Unauthorised if the key is not present or incorrect**
 - statusCode - 401
 - statusCodeDescription - Unauthorized

**A successful (200) call should return the following fields**
 - documentText - the plain text representation of the document
 - statusCode - 200
 - statusCodeDescription - OK

## Operation 3 - wordToMarkdown

This function should take the base64 encoded representation of a word document and return the markdown equivilent.  Make sure the markdown text is formatted nicely so it bares resemblence to the original layout and formatting of the word document.

It should use the same apiKey as Operation 1.

**It should return 401 - Unauthorised if the key is not present or incorrect**
 - statusCode - 401
 - statusCodeDescription - Unauthorized

**A successful (200) call should return the following fields**
 - documentMarkdown - the markdown representation of the document
 - statusCode - 200
 - statusCodeDescription - OK

The code **MUST** be structured in such a way that it is easy to deploy and easy to add extra operations if required.