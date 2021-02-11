# Available Functions

- [print_structured_result](/nornir_scrapli/api_docs/functions/#print_structured_result) -- this function is very similar to the "normal" 
  `print_result` function that now ships with the `nornir_utils` library (historically with nornir "core"), except 
  it contains several  additional arguments, most importantly the `parser` argument allows you to select `textfsm` 
  or `genie` to decide which parser to use to parse the unstructured data stored in the results object. Please see the structured
    results example [here](https://github.com/scrapli/nornir_scrapli/tree/master/examples/structured_data) for more details.
