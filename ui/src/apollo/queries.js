import gql from "graphql-tag";

const projectFragment = gql`
  fragment projectFields on ProjectType {
    id
    name
    title
    ecosystem {
      id
      name
    }
    parentProject {
      name
    }
  }
`;

const GET_ECOSYSTEMS = gql`
  query GetEcosystems($pageSize: Int, $page: Int) {
    ecosystems(pageSize: $pageSize, page: $page) {
      entities {
        id
        name
        title
        description
        projectSet {
          ...projectFields
          subprojects {
            ...projectFields
            subprojects {
              ...projectFields
              subprojects {
                ...projectFields
              }
            }
          }
        }
      }
      pageInfo {
        totalResults
      }
    }
  }
  ${projectFragment}
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
