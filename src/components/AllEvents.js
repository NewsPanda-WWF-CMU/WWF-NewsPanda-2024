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
import csvData from "../data/current-processed-events.csv"; // Update the import to the correct path
import "./AllEvents.css";

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
        placeholder="Search events..."
        style={{
          fontSize: "1.1rem",
          marginBottom: "10px",
        }}
      />
    </span>
  );
};

const AllEventsList = ({ isAbridged }) => {
  const [data, setData] = useState([]);
  useEffect(() => {
    Papa.parse(csvData, {
      download: true,
      header: true,
      complete: (results) => {
        let filteredData = results.data
          .filter((row) => {
            const hasEventTitle = row["Event Title"];
            const hasEventCategory = row["Event Category"];
            if (isAbridged) {
              return hasEventTitle && hasEventCategory;
            }
            return hasEventTitle;
          })
          .sort(
            (a, b) => new Date(b["Event Date"]) - new Date(a["Event Date"])
          );
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
        accessor: "Event Title",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Sources",
        accessor: "Event Urls",
        Cell: ({ value }) =>
          value
            ? value
                .replace("[", "")
                .replace("]", "")
                .split(",")
                .map((url, index) => (
                  <div key={index}>
                    <a
                      href={url.replace("'", "").replace("'", "")}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {url.replace("'", "").replace("'", "")}
                    </a>
                  </div>
                ))
            : null,
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Category",
        accessor: "Event Category",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Summary",
        accessor: "Event Summary",
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Recommended Actions",
        accessor: "Event Actions",
        Cell: ({ value }) =>
          value
            ? value
                .replace("[", "")
                .replace("]", "")
                .split(",")
                .map((action, index) => (
                  <div key={index}>
                    {index + 1}. {action.replace("'", "").replace("'", "")}
                  </div>
                ))
            : null,
        disableSortBy: true, // Disable sorting on this column
      },
    ],
    []
  );

  const abridgedColumns = useMemo(
    () => [
      {
        Header: "Title",
        accessor: "Event Title",
        Cell: ({ row }) => (
          <a
            href={row.original["Event Urls"]}
            target="_blank"
            rel="noopener noreferrer"
          >
            {row.original["Event Title"]}
          </a>
        ),
        disableSortBy: true, // Disable sorting on this column
      },
      {
        Header: "Category",
        accessor: "Event Category",
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
          <h1>All Events</h1>
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

export default AllEventsList;
