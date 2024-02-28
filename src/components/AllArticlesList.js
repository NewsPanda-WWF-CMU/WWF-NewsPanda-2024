import React, { useMemo, useState, useEffect } from "react";
import {
  useTable,
  usePagination,
  useSortBy,
  useGlobalFilter,
  useAsyncDebounce,
} from "react-table";
import Papa from "papaparse";
import Header from "./Header"; // Make sure this is correctly imported
import csvData from "../data/test-last-year-nepal-cleaned.csv"; // Update the import to the correct path
import "./AllArticlesList.css";

// This is a custom filter UI for selecting a unique option from a list
function SelectColumnFilter({
  column: { filterValue, setFilter, preFilteredRows, id },
}) {
  // Calculate the options for filtering using the preFilteredRows
  const options = React.useMemo(() => {
    const options = new Set();
    preFilteredRows.forEach((row) => {
      options.add(row.values[id]);
    });
    return [...options.values()];
  }, [id, preFilteredRows]);

  // Render a multi-select box
  return (
    <select
      value={filterValue}
      onChange={(e) => {
        setFilter(e.target.value || undefined);
      }}
    >
      <option value="">All</option>
      {options.map((option, i) => (
        <option key={i} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}

const GlobalFilter = ({ globalFilter, setGlobalFilter }) => {
  const [value, setValue] = useState(globalFilter);
  const onChange = useAsyncDebounce((value) => {
    setGlobalFilter(value || undefined);
  }, 200);

  return (
    <span className="search-bar">
      Search:{" "}
      <input
        value={value || ""}
        onChange={(e) => {
          setValue(e.target.value);
          onChange(e.target.value);
        }}
        placeholder="Search articles..."
        style={{
          fontSize: "1.1rem",
          marginBottom: "10px",
        }}
      />
    </span>
  );
};

const AllArticlesList = ({ isAbridged }) => {
  const [data, setData] = useState([]);
  useEffect(() => {
    Papa.parse(csvData, {
      download: true,
      header: true,
      complete: (results) => {
        let filteredData = results.data
          .filter((row) => {
            const hasPublishedDate =
              row.publishedAt && new Date(row.publishedAt).getTime() > 0;
            const isLandscapeNotNone = row["Landscape-Location"];
            const isLandscapeNotOther =
              row["Landscape-Location"] !== "Other" &&
              row["Landscape-Location"]?.replace(/ /g, "") !== "Other(Nepal)";
            let hasAuthor = row["author"];
            if (!hasAuthor) {
              row["author"] = row["source_name"];
              hasAuthor = true;
              console.log(row["publishedAt"]);
            }
            if (isAbridged) {
              return (
                hasPublishedDate && isLandscapeNotNone && isLandscapeNotOther
              );
            }
            return hasPublishedDate && isLandscapeNotNone;
          })
          .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
        if (isAbridged) {
          filteredData = filteredData.slice(0, 7);
        }
        setData(filteredData);
      },
    });
  }, [isAbridged]);

  const columns = useMemo(
    () => [
      {
        Header: "Title",
        accessor: "title",
        Cell: ({ row }) => (
          <a href={row.original.url} target="_blank" rel="noopener noreferrer">
            {row.original.title}
          </a>
        ),
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Author",
        accessor: "author",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Date",
        accessor: "publishedAt",
        Cell: ({ value }) => {
          const date = new Date(value);
          return `${date.getDate()}/${
            date.getMonth() + 1
          }/${date.getFullYear()}`;
        },
        disableFilters: true, // Disable column filter for Date, we will use sorting
      },
      {
        Header: "Category Tags",
        accessor: "Category-Tags",
        Cell: ({ value }) =>
          value
            ? value
                .split(",")
                .map((tag) => <span className="badge">{tag.trim()}</span>)
            : "",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Flora and Fauna",
        accessor: "Flora_and_Fauna",
        Cell: ({ value }) =>
          value
            ? value
                .split(",")
                .map((tag) => <span className="badge">{tag.trim()}</span>)
            : "",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Landscape Location",
        accessor: "Landscape-Location",
        Filter: SelectColumnFilter, // A custom select filter component
        filter: "includes",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Relevant to Conservation",
        id: "conservationRelevance",
        accessor: (row) =>
          row["gpt-relevance_to_conservation"] > 0.5 ? "✓" : "✗",
        disableSortBy: true, // Disable sorting on this column
      },
      // Column for Relevance to Infrastructure
      {
        Header: "Relevant to Infrastructure",
        id: "infrastructureRelevance",
        accessor: (row) => (row["gpt-relevance_to_infra"] > 0.5 ? "✓" : "✗"),
        disableSortBy: true, // Disable sorting on this column
      },
    ],
    []
  );

  const abridgedColumns = useMemo(
    () => [
      {
        Header: "Title",
        accessor: "title",
        Cell: ({ row }) => (
          <a href={row.original.url} target="_blank" rel="noopener noreferrer">
            {row.original.title}
          </a>
        ),
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Date",
        accessor: "publishedAt",
        Cell: ({ value }) => {
          const date = new Date(value);
          return `${date.getDate()}/${
            date.getMonth() + 1
          }/${date.getFullYear()}`;
        },
        disableFilters: true, // Disable column filter for Date, we will use sorting
        disableSortBy: true,
      },
      {
        Header: "Landscape Location",
        accessor: "Landscape-Location",
        Filter: SelectColumnFilter, // A custom select filter component
        filter: "includes",
        disableSortBy: true, // Disable sorting on this column
      },
    ],
    []
  );

  const filterTypes = React.useMemo(
    () => ({
      // A simple fuzzy text filter function
      fuzzyText: (rows, id, filterValue) => {
        // Convert the filter value to lowercase
        const lowercasedFilterValue = filterValue.toLowerCase();
        // Filter the rows where the cell value contains the filter value
        return rows.filter((row) => {
          console.log(row);
          // Get the value of the cell for the current column (id)

          const cellValue = row.values[id];
          // Return true if the cellValue is not undefined and contains the filter value
          return cellValue !== undefined
            ? String(cellValue).toLowerCase().includes(lowercasedFilterValue)
            : true;
        });
      },
      // Default text filter: check if row starts with filter value
      text: (rows, id, filterValue) => {
        return rows.filter((row) => {
          const rowValue = row.values[id];
          return rowValue !== undefined
            ? String(rowValue)
                .toLowerCase()
                .startsWith(String(filterValue).toLowerCase())
            : true;
        });
      },
    }),
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    preGlobalFilteredRows,
    setGlobalFilter,
    state,

    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns: !isAbridged ? columns : abridgedColumns,
      data,
      initialState: { pageIndex: 0 },
      filterTypes,
    },
    useGlobalFilter, // Use the useGlobalFilter hook to provide a global filter UI
    useSortBy,
    usePagination
  );

  // We do not show the global filter if there are less than 10 rows
  const showGlobalFilter = preGlobalFilteredRows.length > 10;

  return (
    <>
      {!isAbridged ? (
        <>
          <Header />
          <h1>All Articles</h1>
          {showGlobalFilter && (
            <GlobalFilter
              preGlobalFilteredRows={preGlobalFilteredRows}
              globalFilter={state.globalFilter}
              setGlobalFilter={setGlobalFilter}
            />
          )}
        </>
      ) : null}
      <div className={!isAbridged ? "table-container" : ""}>
        <table {...getTableProps()} className="table">
          <thead>
            {headerGroups.map((headerGroup, idx) => (
              <tr key={idx} {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <th
                    {...column.getHeaderProps(column.getSortByToggleProps())}
                    className={!column.disableSortBy ? "" : "disable-sorting"}
                  >
                    {column.render("Header")}
                    {/* Only show sort indicator if sorting is enabled */}
                    {!column.disableSortBy && !isAbridged ? (
                      column.isSorted ? (
                        column.isSortedDesc ? (
                          <span className="sort-indicator desc">↓</span>
                        ) : (
                          <span className="sort-indicator asc">↑</span>
                        )
                      ) : (
                        <span className="sort-indicator">↕</span>
                      )
                    ) : null}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...getTableBodyProps()}>
            {page.map((row) => {
              prepareRow(row);
              return (
                <tr {...row.getRowProps()}>
                  {row.cells.map((cell, cellIdx) => {
                    return (
                      <td key={cellIdx} {...cell.getCellProps()}>
                        {cell.render("Cell")}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
        {!isAbridged ? (
          <div className="pagination">
            <div className="pagination-controls">
              <button onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
                {"<<"}
              </button>{" "}
              <button
                onClick={() => previousPage()}
                disabled={!canPreviousPage}
              >
                {"<"}
              </button>{" "}
              <button onClick={() => nextPage()} disabled={!canNextPage}>
                {">"}
              </button>{" "}
              <button
                onClick={() => gotoPage(pageCount - 1)}
                disabled={!canNextPage}
              >
                {">>"}
              </button>{" "}
            </div>
            <span>
              Page{" "}
              <strong>
                {pageIndex + 1} of {pageCount}
              </strong>{" "}
            </span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
              }}
            >
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                  Show {pageSize}
                </option>
              ))}
            </select>
          </div>
        ) : null}
      </div>
    </>
  );
};

export default AllArticlesList;
