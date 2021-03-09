import gql from "graphql-tag";

const GET_ECOSYSTEMS = gql`
  query GetEcosystems($pageSize: Int, $page: Int) {
    ecosystems(pageSize: $pageSize, page: $page) {
      entities {
        id
        name
        title
        description
      }
      pageInfo {
        totalResults
      }
    }
  }
`;

const getEcosystems = (apollo, pageSize, page) => {
  const response = apollo.query({
    query: GET_ECOSYSTEMS,
    variables: {
      pageSize,
      page
    }
  });
  return response;
};

export { getEcosystems };
